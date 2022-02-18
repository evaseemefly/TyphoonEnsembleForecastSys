## 前端项目文档

组件  
```js
.  
├── Content  // root父组件
│ ├── ConterMap // router页面 
│ |  ├── TopNavBar
│ |  ├── TyGroupMap  // router-view: /content/TyphoonGroupMap 台风集合预报路径map主页面
│ |  |  ├── TaskRateCard  // 进度card组件
│ |  |  ├── LMap          // leaflet L.map
│ |  |  ├── CurdBtn       // 创建case与查询case按钮
│ |  |  ├── CreateCaseForm  // 默认隐藏的创建caseform
│ |  |  ├── BottomMainBar   // 底部的操作组件
│ |  |  |  ├── BottomRightMainBar   // 底部右侧图例等组件
│ |  |  |  | ├── SwitchBaseMap  // 切换底图
│ |  |  |  | ├── ColorBar       // 动态色标图例
│ |  |  |  ├── TimeBar     // 交互式时间轴组件
│ |  |  ├── OceanMainToolsBar   // 图层加载组件
```