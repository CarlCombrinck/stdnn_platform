import argparse
import os
import warnings
from datetime import datetime

import numpy as np
import torch

import stdnn.evaluation.test_
import stdnn.training.baseline
from stdnn.preprocessing.loader import load_dataset
from stdnn.preprocessing.utils import process_adjacency_matrix
from stdnn.utils import correlation_adjacency_matrix
from stdnn.models.utils import get_model_class

def str2bool(v):
    """
    Converts a string argument to the boolean equivalent

    Parameters
    ----------
    v : Union[bool, str]
        Command line argument value

    Returns
    -------
    bool
    """
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


warnings.filterwarnings("ignore", category=UserWarning)

parser = argparse.ArgumentParser()
parser.add_argument('--model', type=str, default='GWN')
parser.add_argument('--model_module', type=str, default='gwnet')
parser.add_argument('--baseline', type=str2bool, default=False)
parser.add_argument('--baseline_only', type=str2bool, default=False)
# StemGNN arguments
parser.add_argument('--train', type=str2bool, default=True)
parser.add_argument('--evaluate', type=str2bool, default=True)
parser.add_argument('--dataset', type=str, default='JSE_clean_truncated')
parser.add_argument('--window_size', type=int, default=20)
parser.add_argument('--horizon', type=int, default=5)
parser.add_argument('--train_length', type=float, default=6)
parser.add_argument('--valid_length', type=float, default=2)
parser.add_argument('--test_length', type=float, default=2)
parser.add_argument('--epoch', type=int, default=50)
parser.add_argument('--lr', type=float, default=1e-4)
parser.add_argument('--multi_layer', type=int, default=5)
parser.add_argument('--device', type=str, default=('cuda' if torch.cuda.is_available() else 'cpu'))
parser.add_argument('--validate_freq', type=int, default=1)
parser.add_argument('--batch_size', type=int, default=32)
parser.add_argument('--norm_method', type=str, default='z_score')
parser.add_argument('--optimizer', type=str, default='RMSProp')
parser.add_argument('--early_stop', type=str2bool, default=False)
parser.add_argument('--exponential_decay_step', type=int, default=5)
parser.add_argument('--decay_rate', type=float, default=0.5)
parser.add_argument('--dropout_rate', type=float, default=0.5)
parser.add_argument('--leakyrelu_rate', type=int, default=0.2)

# GWN arguments
parser.add_argument('--adj_data', type=str2bool, default=False)
parser.add_argument('--adj_type', type=str, default='double_transition')
parser.add_argument('--gcn_bool', type=str2bool, default=True)
parser.add_argument('--apt_only', type=str2bool, default=True)
parser.add_argument('--adapt_adj', type=str2bool, default=True)
parser.add_argument('--random_adj', type=str2bool, default=True)
parser.add_argument('--channels', type=int, default=32)
parser.add_argument('--in_dim', type=int, default=1)
parser.add_argument('--weight_decay', type=float, default=0.0001)

# MTGNN arguments
parser.add_argument('--build_adj', type=str2bool, default=True)
parser.add_argument('--load_static_feature', type=str2bool, default=False)
parser.add_argument('--cl', type=str2bool, default=True)
parser.add_argument('--gcn_depth', type=int, default=2)
parser.add_argument('--subgraph_size', type=int, default=20)
parser.add_argument('--node_dim', type=int, default=40)
parser.add_argument('--dilation_exponential', type=int, default=1)
parser.add_argument('--conv_channels', type=int, default=32)
parser.add_argument('--residual_channels', type=int, default=32)
parser.add_argument('--skip_channels', type=int, default=64)
parser.add_argument('--end_channels', type=int, default=128)
parser.add_argument('--layers', type=int, default=3)
parser.add_argument('--clip', type=int, default=5)
parser.add_argument('--step_size1', type=int, default=2500)
parser.add_argument('--step_size2', type=int, default=100)
parser.add_argument('--seed', type=int, default=101)
parser.add_argument('--prop_alpha', type=float, default=0.05)
parser.add_argument('--tanh_alpha', type=float, default=3)
parser.add_argument('--splits', type=int, default=1)

# LSTM arguments
parser.add_argument('--lstm_layers', type=int, default=100)
parser.add_argument('--lstm_node', type=int, default=0)

args = parser.parse_args()
print(f'Training Configuration: {args}')
print()
result_train_file = os.path.join('output', args.model, args.dataset, str(args.window_size), str(args.horizon), 'train')
baseline_train_file = os.path.join('output', 'lstm', args.dataset, str(args.window_size), str(args.horizon), 'train')
if not os.path.exists(result_train_file):
    os.makedirs(result_train_file)
if not os.path.exists(baseline_train_file):
    os.makedirs(baseline_train_file)

train_data, valid_data, test_data = load_dataset(args.dataset, args.train_length, args.valid_length, args.test_length)
args.node_cnt = train_data.shape[1]

if args.adj_data:
    if args.model == 'GWN':
        adj_matrix = process_adjacency_matrix(os.path.join('data', args.dataset + '.csv'), args.adj_type)
        args.supports = [torch.tensor(i).to(args.device) for i in adj_matrix]
        if args.apt_only:
            args.supports = None
            args.adj_init = None
        else:
            if args.random_adj:
                args.adj_init = None
            else:
                args.adj_init = args.supports[0]

    if args.model == 'MTGNN':
        adj_matrix = correlation_adjacency_matrix(os.path.join('data', args.dataset + '.csv')).astype(np.float32)
        adj_matrix = torch.tensor(adj_matrix) - torch.eye(args.node_cnt)
        args.adj_matrix = adj_matrix.to(args.device)
else:
    args.adj_matrix = None
    args.adj_init = None
    args.supports = None

torch.manual_seed(0)
if __name__ == '__main__':

    Model = get_model_class(args.model_module, args.model)

    # TODO refactor to use **args instead of passing individual args
    model = Model(device=args.device, node_cnt=args.node_cnt, dropout=args.dropout_rate,
                    supports=args.supports, gcn_bool=args.gcn_bool, adapt_adj=args.adapt_adj,
                    adj_init=args.adj_init, in_dim=args.in_dim, out_dim=args.horizon,
                    residual_channels=args.channels, dilation_channels=args.channels,
                    skip_channels=args.channels * 8, end_channels=args.channels * 16)

    if args.train:
        if args.baseline:
            _ = stdnn.training.baseline.train(train_data, valid_data, args, baseline_train_file)
        if not args.baseline_only:
            try:
                before_train = datetime.now().timestamp()
                _ = model.train_model(train_data, valid_data, args, result_train_file)
                after_train = datetime.now().timestamp()
                hours, rem = divmod(after_train - before_train, 3600)
                minutes, seconds = divmod(rem, 60)
                print("Train Time: ""{:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds))
            except KeyboardInterrupt:
                print('-' * 99)
                print('Exiting Early')
    if args.evaluate:
        if args.baseline:
            stdnn.evaluation.test_.baseline_test(test_data, args, baseline_train_file)
        before_evaluation = datetime.now().timestamp()
        if not args.baseline_only:
            model.test_model(test_data, args, result_train_file)
            after_evaluation = datetime.now().timestamp()
            hours, rem = divmod(after_evaluation - before_evaluation, 3600)
            minutes, seconds = divmod(rem, 60)
            print("Evaluation Time: ""{:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds))
    print('done')
