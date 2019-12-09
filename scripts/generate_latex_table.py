import os
from core.adv_utlis import *
from core.portfolio import *
from scipy.stats import ttest_1samp

# file_name = 'MV_Sigma_Cur_55.p'


def gen_latex(file_name_1, file_name_2, out_path=None):
    panel_path_1 = os.path.join(config.panel_data_directory, file_name_1)
    panel_path_2 = os.path.join(config.panel_data_directory, file_name_2)
    cur_panel_1 = PanelData.load_pickle(panel_path_1)
    cur_panel_2 = PanelData.load_pickle(panel_path_2)
    index = ['Small', '2', '3', '4', 'Big', 'All']
    columns = ['Low', '2', '3', '4', 'High', '1-5', '(t)', '(p)']
    out_panel = pd.DataFrame(index=index, columns=columns)
    cur_list = []
    ret_1 = period_ret_all(cur_panel_1.ret, config.month_split)
    ret_2 = period_ret_all(cur_panel_2.ret, config.month_split)

    for idx in range(len(cur_panel_1.group) + len(cur_panel_2.group)):
        if idx < len(cur_panel_1.group):
            ret = ret_1
            ret_idx = idx
        else:
            ret = ret_2
            ret_idx = idx - len(cur_panel_1.group)
        cur_ret = ret.iloc[:, ret_idx]
        i = idx // 5
        j = idx % 5
        if j == 0:
            cur_list = [cur_ret]
        elif j == 4:
            cur_list.append(cur_ret)
            cur_list.append(cur_list[0] - cur_ret)
            out_panel.iloc[i, 5] = cur_list[-1].mean() * 100
            out_panel.iloc[i, 6], out_panel.iloc[i, 7] = ttest_1samp(cur_list[-1], popmean=0)
        else:
            cur_list.append(cur_ret)
        out_panel.iloc[i, j] = cur_ret.mean() * 100
    if out_path is not None:
        out_panel.to_latex(out_path, float_format="{:0.2f}".format)
    print(out_panel)
    return out_panel


dir = '/Users/oranbebai/PHD/Finance/Papers/ShortSellContrain/Tables'

gen_latex('MV_Sigma_Cur_55.p', 'Sigma_Cur_5.p', os.path.join(dir, 'Sigma_Cur.tex'))
gen_latex('MV_Sigma_Pre_55.p', 'Sigma_Pre_5.p', os.path.join(dir, 'Sigma_Pre.tex'))

print(1)