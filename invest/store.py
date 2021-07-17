import pandas as pd
# import invest.calculator.ratios as ratios
# import invest.calculator.threshold as threshold


class Store:
    def __init__(self, main_data, all_companies,
                 consumer_companies,
                 general_companies, margin_of_safety, beta, years):
        self.main_data = main_data
        self.all_companies = all_companies
        self.consumer_companies = consumer_companies
        self.general_companies = general_companies
        self.margin_of_safety = margin_of_safety
        self.beta = beta
        self.years = years
        self.process(self)

    # newDf
    column_names = ["negative_earnings", "negative_shareholders_equity", "beta_classify", "acceptable_stock",
                    "current_PE_relative_share_market_to_historical", "current_PE_relative_share_sector_to_historical",
                    "forward_PE_current_to_historical", "roe_vs_coe",
                    "growth_cagr_vs_inflation", "relative_debt_to_equity"]
    share_data_frame = pd.DataFrame(columns=column_names)

    def process(self):

    # calculate ratios
        for company in self.all_companies:
            indexes = []
            #preprocessing to gets lists etc
            year = 2012
            years = 2017 #year after data value being used , this case is using 2016 latest as final
            for year in years:
                mask = (self.main_data['Date'] > str(year) +'-'+ '01-01') & (self.main_data['date'] <= year + '12-31')
                company_df = self.main_data.loc[self.main_data['Name'] == company and mask]
                last_row = company_df.last_valid_index()
                indexes.append(last_row)
                # add eps value to list
                year += 1
        print(indexes)
            #
            #
            # # only use this companies data
            # historic_earnings_growth_rate = ratios.historic_earnings_growth_rate(eps_list, 3)
            # historic_earnings_cagr = ratios.historic_earnings_cagr(eps_n, eps_prev_x, x)
            # historic_price_to_earnings_share = ratios.historic_price_to_earnings_share(price_list, eps_list)
            # forward_earnings_current_year = ratios.forward_earnings(eps_latest,
            #                                                         historic_earnings_growth_rate)  # for the current
            # # forward earnings for 3 years ago
            # historic_earnings_growth_rate_past = ratios.historic_earnings_growth_rate(eps_list_from_past,
            #                                                                           3)  # intermediate, list from past can be 2013 since year is 3
            # forward_earnings_past = ratios.forward_earnings(eps_past_year,
            #                                                 historic_earnings_growth_rate_past)  # intermediate
            # forward_earnings_cagr = ratios.forward_earnings_cagr(forward_earnings_current_year, forward_earnings_past, 3)
            # forward_price_to_earnings = ratios.forward_price_to_earnings(price, forward_earnings_current_year)
            #
            # if company in self.consumer_companies:
            #     pe_relative_sector = ratios.pe_relative_sector(historic_price_to_earnings_share,
            #                                                    consumer_sector_data)  # consumer related data for sector for year. This value is historical
            #     pe_relative_market = ratios.pe_relative_market(historic_price_to_earnings_share,
            #                                                    consumer_market_data)  # consumer related for market pass in for year
            # else:
            #     pe_relative_sector = ratios.pe_relative_sector(historic_price_to_earnings_share,  # historical
            #                                                    general_industrials_sector_data)  # general related data for sector for year
            #     pe_relative_market = ratios.pe_relative_market(historic_price_to_earnings_share,  # historical
            #                                                    general_industrials_market_data)  # general related for market pass in for year
            #
            # # return_on_equity = # only get ROE from main data for 2017
            # cost_of_equity = ratios.cost_of_equity(market_rate_of_return, risk_free_rate_of_return, beta)
            # relative_debt_equity = ratios.relative_debt_to_equity(d_e, d_e_industry)  # debt equity is from data directly
            #
            # # threshold
            # negative_earnings = threshold.negative_earnings(forward_earnings_current_year)
            # negative_shareholders_equity = threshold.negative_shareholders_equity(shareholders_equity)  # need value
            # beta_classify = threshold.beta_classify(share_beta, beta)
            # acceptable_stock = threshold.acceptable_stock(negative_earnings, negative_shareholders_equity, beta_classify)
            #
            # if acceptable_stock == True:  # only if stock is investable do you continue the process
            #
            #     pe_current_share_market = ratios.current_pe_market(current_share_pe,
            #                                                        current_market_pe)  # PE value for this year
            #     pe_current_share_sector = ratios.current_pe_sector(current_share_pe,
            #                                                        current_sector_pe)  # PE value for this year
            #     pe_relative_market = threshold.current_PE_relative_share_market(margin_of_safety, pe_current_share_market,
            #                                                                     pe_relative_market)  # current share PE must be passed in, current market PE must be passed in
            #
            #     pe_relative_sector = threshold.current_PE_relative_share_sector(margin_of_safety, pe_current_share_sector,
            #                                                                     pe_relative_sector)
            #
            #     forward_pe = threshold.forward_PE(margin_of_safety, forward_price_to_earnings,
            #                                       historic_price_to_earnings_share)
            #
            #     roe_coe = threshold.roe_coe(margin_of_safety, roe, coe)  # roe from data , need to find coe
            #     cagr_inflation = threshold.cagr_inflation(margin_of_safety, historic_earnings_cagr,
            #                                               inflation)  # or use forecast consensus if available
            #     relative_debt_to_equity = threshold.relative_debt_to_equity(margin_of_safety, relative_debt_equity)
            #
            #     # add row to dataframe
            #     company_row = {negative_earnings, negative_shareholders_equity, beta_classify, acceptable_stock,
            #                    pe_relative_market,
            #                    pe_relative_sector, forward_pe, roe_coe, cagr_inflation, relative_debt_to_equity}
            #     shares_data_frame = shares_data_frame.append(company_row, ignore_index=True)
            # else:
            #     company_row = {negative_earnings, negative_shareholders_equity, beta_classify,
            #                    acceptable_stock}  # only these values are calculated
            #     shares_data_frame = shares_data_frame.append(company_row, ignore_index=True)
