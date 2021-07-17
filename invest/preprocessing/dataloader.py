import pandas as pd
companies= ["ADVTECH", "CITY LODGE HOTELS", "CLICKS GROUP", "CURRO HOLDINGS", "CASHBUILD", "FAMOUS BRANDS", "ITALTILE",
          "LEWIS GROUP", "MR PRICE GROUP", "MASSMART", "PICK N PAY STORES", "SHOPRITE", "SPAR GROUP",
          "SUN INTERNATIONAL", "SPUR", "THE FOSCHINI GROUP", "TRUWORTHS INTL", "TSOGO SUN", "WOOLWORTHS HDG",
          "AFRIMAT","BARLOWORLD","BIDVEST GROUP","GRINDROD","HUDACO","IMPERIAL","INVICTA","KAP INDUSTRIAL","MPACT", "MURRAY & ROBERTS",
          "NAMPAK","PPC","RAUBEX GROUP","REUNERT","SUPER GROUP","TRENCOR","WLSN.BAYLY HOLMES-OVCON"]
def load_data():
    df = pd.read_csv("/Users/insaafdhansay/desktop/cogspms/invest/preprocessing/data/invest_data.csv", sep=';')
    mask = (df['Date'] > '2012-01-01')
    int_df = df.loc[df['Name'].isin(companies)] #only use 36 companies
    final_df = int_df.loc[mask]
    print(final_df['Name'].unique())
    print(final_df['Name'].nunique())
    print(final_df)
def load_dummy_data():
    df = pd.read_csv("/Users/insaafdhansay/desktop/cogspms/invest/preprocessing/data/dummy_data.csv", sep=';')
    print(df)
    return df




# functions to pass it data for X period of time- one year
#mask = (df['Date'] > '2012-1-1') & (df['date'] <= '2000-6-10')