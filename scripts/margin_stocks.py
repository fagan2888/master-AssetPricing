from core.allocate import *
from core.utils import *
from core.adv_utlis import *
from core.regression import *

"""
This script is used for testing the difference of return between portfolios formed by short saleable stocks and 
non-short saleable stocks. Fama-french regression is performed for each portfolio with MKT, SMB, HML, adjTover or sigma 
factor. 
"""
# Load daily return and market value of all stocks
all_stocks_data_path = os.path.join(config.temp_data_path, 'AllStocksPortfolio.p')
all_stocks_data = Portfolio.load_pickle(all_stocks_data_path)

# Generate month tags and month split from 2010-04 to 2019-07
period = ('2010-04', '2019-07')
month_split = get_split(period)[0]
month_tag = get_split(period)[3]

# Read short sell target
saleable_target_path = os.path.join(config.feature_directory, 'ShortSellTarget.csv')
saleable_pd = pd.read_csv(saleable_target_path, index_col=0)

# period_to_tickers dictionary of short sell targets
saleable_groups = {}
for date, row in saleable_pd.iterrows():
    idx = month_tag.index(date)
    key = (month_tag[idx], month_tag[idx + 1])
    saleable_groups[key] = row[row == 1.0].index.tolist()

# period_to_tickers dictionary of non short sell targets
non_saleable_groups = {}
for key, tickers in saleable_groups.items():
    non_tickers = [ticker for ticker in config.A_lists if ticker not in tickers]
    non_saleable_groups[key] = non_tickers

# Set path of features
adjTover_path = os.path.join(config.feature_directory, 'M_AdjTover.csv')
mv_path = os.path.join(config.feature_directory, 'M_MktV.csv')
sigma_path = os.path.join(config.feature_directory, 'M_Sigma.csv')

# Add features to allocator
saleable_allocator_path = os.path.join(config.temp_data_path, 'saleable_allocator.p')
if not os.path.exists(saleable_allocator_path):
    saleable_allocator = Allocate(tickers=config.A_lists, periods=month_split, period_to_tickers=saleable_groups)
    saleable_allocator.to_pickle(saleable_allocator_path)
else:
    saleable_allocator = Allocate.load_pickle(saleable_allocator_path)
saleable_allocator = update_allocator(saleable_allocator_path, ('mv', mv_path), ('adjTover', adjTover_path), ('sigma', sigma_path))

# Allocate saleable stocks in to 5 groups/5*5 groups according to adjTover/MV-adjTover
adjTover_5_panel = gen_panel('adjTover_5_panel', saleable_allocator, (['adjTover'], [(0, 0.2, 0.4, 0.6, 0.8, 1)]), all_stocks_data, period)

adjTover_MV_55_panel = gen_panel('adjTover_MV_55_panel', saleable_allocator,
                                 (['mv', 'adjTover'], [(0, 0.2, 0.4, 0.6, 0.8, 1), (0, 0.2, 0.4, 0.6, 0.8, 1)]), all_stocks_data, period)

non_saleable_allocator_path = os.path.join(config.temp_data_path, 'non_saleable_allocator.p')
if not os.path.exists(non_saleable_allocator_path):
    non_saleable_allocator = Allocate(tickers=config.A_lists, periods=month_split, period_to_tickers=non_saleable_groups)
    non_saleable_allocator.to_pickle(non_saleable_allocator_path)
else:
    non_saleable_allocator = Allocate.load_pickle(non_saleable_allocator_path)
non_saleable_allocator = update_allocator(non_saleable_allocator_path, ('mv', mv_path), ('adjTover', adjTover_path), ('sigma', sigma_path))
# Allocate non_saleable stocks into 5/5*5 groups according to adjTover/MV-adjTover factors
nonSale_adjTover_5_panel = gen_panel('nonSale_adjTover_5_panel_path', non_saleable_allocator,
                                     (['adjTover'], [(0, 0.2, 0.4, 0.6, 0.8, 1)]), all_stocks_data, period)

nonSale_adjTover_MV_55_panel = gen_panel('nonSale_adjTover_MV_55_panel', non_saleable_allocator,
                                         (['mv', 'adjTover'], [(0, 0.2, 0.4, 0.6, 0.8, 1), (0, 0.2, 0.4, 0.6, 0.8, 1)]), all_stocks_data, period)
# Load trade dates
trd_cale_path = os.path.join(config.raw_directory, 'TRD_Cale.txt')
trade_dates = get_trade_dates(trd_cale_path, period)

# Load risk free data
rf_path = os.path.join(config.raw_directory, 'TRD_Nrrate.txt')
rf_month = get_rf_rate(rf_path, period, mode='m')

# Load 5 factor data
# Index:    date;
# Columns: 'RiskPremium1', 'RiskPremium2', 'SMB1', 'SMB2', 'HML1', 'HML2', 'RMW1', 'RMW2', 'CMA1', 'CMA2';
factor_path = os.path.join(config.raw_directory, 'STK_MKT_FivefacDay.txt')
factors = get_factors(factor_path, period, mode='d')
adjTover_factor_path = os.path.join(config.factor_path, 'adjTover.csv')
factors['adjTover'] = pd.read_csv(adjTover_factor_path, index_col=0)


# adjTover_5_panel, adjTover_MV_55_panel, nonSale_adjTover_5_panel, nonSale_adjTover_MV_55_panel
reg(adjTover_5_panel, x)
