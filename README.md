# CL vs BRENTOIL 价差数据

这个仓库用于保存并展示来自 **Hyperliquid `xyz` 市场** 的价格与价差数据：

- `xyz:CL`
- `xyz:BRENTOIL`

当前仓库已经支持：

1. **小时级数据（主展示）**
2. **日线数据（保留）**
3. **多次重复抓取更新**
4. 自动生成 CSV / JSON / 图表

---

## 数据来源

- API：`https://api.hyperliquid.xyz/info`
- 数据接口：`candleSnapshot`
- 市场：`dex = xyz`

当前抓取两个周期：

- `1h`：小时级数据
- `1d`：日线数据

说明：
- `xyz:CL` 的历史比 `xyz:BRENTOIL` 更长
- 价差数据使用两者的**时间交集**生成
- 因此最终展示长度取决于两者重叠区间

---

## 仓库文件

### 脚本
- `update_data.py`：抓取并更新全部数据

### 小时级
- `clk26_bzm26_hourly_spread.csv`
- `data_hourly.json`

### 日线级
- `clk26_bzm26_daily_spread.csv`
- `data_daily.json`

### 兼容文件
- `data.json`：当前默认指向小时级图表数据

### 页面
- `index.html`：图表页面

---

## 当前字段说明

CSV 中保留了完整 OHLC：

- `bucket`：时间桶（UTC）
- `cl_open` / `cl_high` / `cl_low` / `cl_close`
- `bren_open` / `bren_high` / `bren_low` / `bren_close`
- `spread_abs_bren_minus_cl`
- `spread_pct_vs_cl`

其中：
- 绝对价差 = `BRENTOIL_close - CL_close`
- 相对价差 = `(BRENTOIL_close - CL_close) / CL_close`

---

## 如何更新数据

在仓库目录运行：

```bash
python3 update_data.py
```

脚本会自动：

1. 拉取 `xyz:CL` 的 `1h` 和 `1d` 数据
2. 拉取 `xyz:BRENTOIL` 的 `1h` 和 `1d` 数据
3. 计算两个周期下的重叠价差
4. 更新：
   - `clk26_bzm26_hourly_spread.csv`
   - `clk26_bzm26_daily_spread.csv`
   - `data_hourly.json`
   - `data_daily.json`
   - `data.json`

这意味着仓库天然支持：
- **反复更新**
- **以后继续追加新数据**
- **页面自动读取最新结果**

---

## 图表说明

打开：

- `index.html`

当前页面默认读取：
- `data.json`

而 `data.json` 现在默认映射为：
- **小时级数据**

页面展示：

1. 上图：CL 与 BRENTOIL 收盘价
2. 中图：绝对价差
3. 下图：相对价差 %

支持：
- 缩放
- 拖动
- 鼠标悬停查看数值
- 范围选择

---

## 当前实际可用长度

按当前抓取结果：

### 日线
- `xyz:CL`：77 根
- `xyz:BRENTOIL`：20 根
- 重叠：20 根

### 小时线
- `xyz:CL`：1812 根
- `xyz:BRENTOIL`：442 根
- 重叠：442 根

所以如果你的目标是“尽可能拿到更长的数据”，当前仓库应以：
- **小时级数据为主**
- 日线作为辅助保留

---

## 说明

如果 Hyperliquid 后续提供更长的 `xyz:BRENTOIL` 历史，重新执行：

```bash
python3 update_data.py
```

数据长度会自动变长，无需额外改代码。
