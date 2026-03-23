# CL vs BRENTOIL 日线价差数据

这个仓库用于保存并展示来自 **Hyperliquid `xyz` 市场** 的日线数据与价差数据：

- `xyz:CL`
- `xyz:BRENTOIL`

当前仓库支持：

1. **重复抓取最新数据**
2. 自动生成最新 CSV
3. 自动生成图表所需的 `data.json`
4. 用网页直接展示价格与价差图

---

## 数据来源

- API: `https://api.hyperliquid.xyz/info`
- 数据类型：`candleSnapshot`
- 周期：`1d`
- 市场：`dex = xyz`

说明：
- `xyz:CL` 的历史长度目前比 `xyz:BRENTOIL` 更长
- 价差表使用两者 **日期交集** 生成
- 因此当前 CSV 代表的是两者都存在数据的重叠区间

---

## 仓库文件

- `update_data.py`：抓取并更新数据的脚本
- `clk26_bzm26_daily_spread.csv`：日线收盘价与价差表
- `data.json`：图表使用的结构化数据
- `index.html`：图表页面

---

## CSV 字段说明

- `date`：日期（UTC）
- `cl_close`：`xyz:CL` 日线收盘价
- `bren_close`：`xyz:BRENTOIL` 日线收盘价
- `spread_abs_bren_minus_cl`：绝对价差 = `BRENTOIL - CL`
- `spread_pct_vs_cl`：相对价差 = `(BRENTOIL - CL) / CL`

---

## 如何更新数据

在仓库目录执行：

```bash
python3 update_data.py
```

脚本会：

1. 从 Hyperliquid 拉取 `xyz:CL` 全部可用日线
2. 从 Hyperliquid 拉取 `xyz:BRENTOIL` 全部可用日线
3. 计算两者重叠区间的日线价差
4. 覆盖更新：
   - `clk26_bzm26_daily_spread.csv`
   - `data.json`

这意味着它天然支持**多次拿取**：
- 想刷新就再次运行脚本即可
- 不需要手动改图表数据

---

## 图表说明

打开：

- `index.html`

页面会读取 `data.json` 并展示：

1. 上图：`CL` 与 `BRENTOIL` 日线收盘价
2. 中图：绝对价差 `BRENTOIL - CL`
3. 下图：相对价差 `%`

支持：
- 鼠标悬停查看数值
- 缩放
- 拖动
- 范围选择

---

## 当前已知情况

截至当前版本：
- `xyz:CL` 的可用日线更长
- `xyz:BRENTOIL` 的可用日线较短
- 因此最终重叠区间从 `2026-03-04` 开始

如果 Hyperliquid 后续补充更早的 `xyz:BRENTOIL` 历史数据，重新运行脚本后仓库数据会自动变长。
