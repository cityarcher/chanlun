# 可视化工具文档

本目录包含两个可视化工具的详细文档：

## 📚 文档列表

1. [enhanced_visualizer.md](enhanced_visualizer.md) - Matplotlib可视化工具
   - 鼠标悬停交互
   - 完整的笔绘制功能
   - 支持导出HTML文件

2. [plotly_visualizer.md](plotly_visualizer.md) - Plotly可视化工具
   - 丰富的交互功能（拖拽缩放、hover信息、Y轴调节）
   - 现代化的界面设计
   - 支持生成独立的HTML文件

## 🎯 工具对比

| 特性 | Matplotlib版 | Plotly版 |
|-----|------------|----------|
| 交互性 | 鼠标悬停 | 拖拽缩放 + hover + Y轴调节 |
| 性能 | 较好（适合大数据） | 优秀（现代浏览器优化） |
| 导出 | 需要mpld3库 | 原生支持HTML |
| 界面 | 经典风格 | 现代风格 |
| 浏览器兼容 | 良好 | 优秀 |
| 学习曲线 | 简单 | 中等 |
| 推荐场景 | 快速查看 | 深度分析 |

## 💡 选择建议

### 使用Matplotlib版，如果：
- 需要快速查看结果
- 数据量较大
- 系统资源有限
- 习惯传统界面

### 使用Plotly版，如果：
- 需要丰富的交互功能
- 需要分享图表
- 需要嵌入网页
- 追求更好的视觉效果

## 🔗 快速链接

- [Enhanced Visualizer 详细文档](enhanced_visualizer.md)
- [Plotly Visualizer 详细文档](plotly_visualizer.md)
- [缠论分析主程序](../baostock_chanlun.md)
- [Mootdx分析主程序](../mootdx_chanlun.md)
