from __future__ import annotations

import argparse
import csv
import json
import os
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
	<meta charset="UTF-8" />
	<meta name="viewport" content="width=device-width, initial-scale=1.0" />
	<title>{title}</title>
	{vis_script_tags}
	<style>
		* {{
			box-sizing: border-box;
		}}
		:root {{
			--bg-0: #f1f5f9;
			--bg-1: #e2e8f0;
			--panel: rgba(255, 255, 255, 0.85);
			--line: #cbd5e1;
			--accent: #0ea5e9;
			--accent-soft: #bae6fd;
			--text: #0f172a;
			--text-light: #64748b;
		}}
		body {{
			margin: 0;
			font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Microsoft YaHei", sans-serif;
			background: linear-gradient(135deg, var(--bg-0), var(--bg-1));
			color: var(--text);
			height: 100vh;
			overflow: hidden;
			line-height: 1.5;
		}}
		.topbar {{
			padding: 16px 24px;
			background: var(--panel);
			border-bottom: 1px solid rgba(255, 255, 255, 0.5);
			position: sticky;
			top: 0;
			z-index: 10;
			backdrop-filter: blur(12px);
			-webkit-backdrop-filter: blur(12px);
			display: flex;
			justify-content: space-between;
			align-items: center;
			gap: 16px;
			box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
		}}
		.title {{
			margin: 0;
			font-size: 22px;
			font-weight: 800;
			color: #0284c7;
			letter-spacing: 0.5px;
		}}
		.meta {{
			margin-top: 4px;
			font-size: 13px;
			color: var(--text-light);
			font-weight: 500;
		}}
		.layout {{
			display: grid;
			grid-template-columns: minmax(0, 1fr) minmax(320px, 380px);
			height: calc(100vh - 76px);
			min-width: 0;
		}}
		#graph {{
			width: 100%;
			height: 100%;
			min-width: 0;
			min-height: 0;
			background: radial-gradient(circle at 15% 20%, #ffffff 0%, #f4f9ff 45%, #e6f3ff 100%);
		}}
		.graph-error {{
			padding: 16px;
			margin: 16px;
			border: 1px solid #fecdd3;
			border-radius: 12px;
			background: #fff1f2;
			color: #be123c;
			font-size: 14px;
			line-height: 1.6;
			box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.05);
		}}
		.sidebar {{
			border-left: 1px solid var(--line);
			background: rgba(255, 255, 255, 0.4);
			backdrop-filter: blur(10px);
			-webkit-backdrop-filter: blur(10px);
			overflow-y: auto;
			overflow-x: hidden;
			padding: 20px;
			display: grid;
			gap: 16px;
			min-width: 0;
			width: 100%;
			align-content: start;
		}}
		.card {{
			border: 1px solid rgba(255, 255, 255, 0.7);
			border-radius: 16px;
			padding: 20px;
			background: rgba(255, 255, 255, 0.9);
			min-width: 0;
			box-shadow: 0 4px 15px -1px rgb(0 0 0 / 0.03);
			backdrop-filter: blur(8px);
			transition: transform 0.2s ease, box-shadow 0.2s ease;
		}}
		.card:hover {{
			transform: translateY(-2px);
			box-shadow: 0 8px 20px -2px rgb(0 0 0 / 0.06);
		}}
		.card h3 {{
			margin: 0 0 16px;
			font-size: 16px;
			font-weight: 700;
			color: #0369a1;
			display: flex;
			align-items: center;
			gap: 8px;
		}}
		.card h3::before {{
			content: '';
			display: inline-block;
			width: 4px;
			height: 1em;
			background: var(--accent);
			border-radius: 4px;
		}}
		.row {{
			display: grid;
			gap: 8px;
			margin-top: 12px;
		}}
		label {{
			font-size: 13px;
			color: #334155;
			font-weight: 500;
		}}
		input, select, button {{
			font-family: inherit;
			font-size: 13px;
		}}
		input, select {{
			padding: 10px 12px;
			border: 1px solid #94a3b8;
			border-radius: 8px;
			outline: none;
			background: rgba(255, 255, 255, 0.9);
			width: 100%;
			transition: all 0.2s ease;
		}}
		input:focus, select:focus {{
			border-color: var(--accent);
			box-shadow: 0 0 0 3px var(--accent-soft);
			background: #ffffff;
		}}
		button {{
			padding: 10px 16px;
			border: 1px solid #cbd5e1;
			background: #f8fafc;
			border-radius: 8px;
			cursor: pointer;
			color: #334155;
			font-weight: 600;
			width: 100%;
			transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
		}}
		button:hover {{
			background: #f1f5f9;
			border-color: #94a3b8;
			transform: translateY(-1px);
			box-shadow: 0 2px 4px rgb(0 0 0 / 0.05);
		}}
		button.primary {{
			background: var(--accent);
			color: #fff;
			border: none;
			box-shadow: 0 2px 8px rgba(14, 165, 233, 0.3);
		}}
		button.primary:hover {{
			background: #0284c7;
			box-shadow: 0 4px 12px rgba(14, 165, 233, 0.4);
		}}
		.actions {{
			display: grid;
			grid-template-columns: 1fr 1fr;
			gap: 12px;
			margin-top: 4px;
		}}
		.component-list {{
			max-height: 160px;
			overflow-y: auto;
			border: 1px dashed #94a3b8;
			border-radius: 8px;
			padding: 8px;
			display: grid;
			gap: 8px;
			background: rgba(248, 250, 252, 0.6);
		}}
		.component-item {{
			display: flex;
			align-items: center;
			gap: 8px;
			font-size: 13px;
			padding: 6px;
			border-radius: 6px;
			background: rgba(255, 255, 255, 0.5);
			transition: background 0.2s;
		}}
		.component-item:hover {{
			background: rgba(255, 255, 255, 0.9);
			box-shadow: 0 1px 3px rgb(0 0 0 / 0.05);
		}}
		.hint {{
			font-size: 12px;
			color: var(--text-light);
			line-height: 1.4;
		}}
		@media (max-width: 960px) {{
			.layout {{
				grid-template-columns: 1fr;
				height: auto;
			}}
			#graph {{
				height: 62vh;
			}}
			.sidebar {{
				border-left: none;
				border-top: 1px solid var(--line);
				width: 100%;
			}}
		}}
		.small {{
			font-size: 13px;
			color: var(--text-light);
			font-weight: 500;
		}}
	</style>
</head>
<body>
	<div class="topbar">
		<div>
			<h1 class="title">{title}</h1>
			<div class="meta" id="metaStats">节点数: {node_count} | 关系数: {edge_count} | 图谱分区: {component_count}</div>
		</div>
		<div class="small">交互模式: 侧边栏创建 + 搜索过滤 + 分区显隐</div>
	</div>
	<div class="layout">
		<div id="graph"></div>
		<aside class="sidebar">
			<section class="card">
				<h3>图谱分区控制</h3>
				<div class="hint">完全不相关的子图会自动分区显示，可单独显隐。</div>
				<div class="actions" style="margin-top:8px;">
					<button class="primary" id="enablePagedMode">按页浏览</button>
					<button id="enableOverviewMode">总览模式</button>
				</div>
				<div class="row" style="margin-top:8px;">
					<label for="pageComponentSelect">分区页码</label>
					<select id="pageComponentSelect"></select>
					<div class="actions">
						<button id="prevPageBtn">上一页</button>
						<button id="nextPageBtn">下一页</button>
					</div>
					<div class="small" id="pageInfo">分页模式已开启</div>
				</div>
			</section>

			<section class="card">
				<h3>节点搜索</h3>
				<div class="row">
					<label for="searchInput">关键词</label>
					<input id="searchInput" type="text" placeholder="输入节点名称关键词" />
					<div class="actions">
						<button class="primary" id="searchBtn">过滤显示</button>
						<button id="clearSearchBtn">清空搜索</button>
					</div>
					<div class="small" id="searchInfo">当前未启用搜索过滤</div>
				</div>
			</section>

			<section class="card">
				<h3>添加节点</h3>
				<div class="row">
					<label for="newNodeLabel">节点名称</label>
					<input id="newNodeLabel" type="text" placeholder="例如：音频中间件" />
					<label for="newNodeDesc">节点描述（可选）</label>
					<input id="newNodeDesc" type="text" placeholder="用于悬浮提示" />
					<button class="primary" id="addNodeBtn">新增节点</button>
				</div>
			</section>

			<section class="card">
				<h3>添加关系</h3>
				<div class="row">
					<label for="relSource">起点节点</label>
					<input id="relSource" list="nodeNameList" type="text" placeholder="输入节点名称" />
					<label for="relTarget">终点节点</label>
					<input id="relTarget" list="nodeNameList" type="text" placeholder="输入节点名称" />
					<label for="relLabel">关系名称</label>
					<input id="relLabel" type="text" placeholder="例如：支持/依赖/提升" />
					<label for="relDirection">关系类型</label>
					<select id="relDirection">
						<option value="directed">有向关系</option>
						<option value="undirected">无向关系</option>
					</select>
					<button class="primary" id="addRelationBtn">新增关系</button>
				</div>
			</section>

			<section class="card">
				<h3>保存与导出</h3>
				<div class="hint">先在前端临时编辑，再按需导出为文件。</div>
				<div class="actions" style="margin-top:8px;">
					<button id="exportJsonBtn">导出 JSON</button>
					<button id="exportCsvBtn">导出 CSV</button>
				</div>
			</section>

			<datalist id="nodeNameList" style="display:none;"></datalist>
		</aside>
	</div>
	<script>
		if (typeof vis === "undefined") {{
			const graph = document.getElementById("graph");
			graph.innerHTML = '<div class="graph-error">图谱渲染库 vis-network 加载失败。<br/>请检查网络后刷新页面，或稍后重试。</div>';
			throw new Error("vis-network failed to load from CDN sources");
		}}

		const initialNodes = {nodes};
		const initialEdges = {edges};

		let allNodes = initialNodes.map((n) => ({{ ...n }}));
		let allEdges = initialEdges.map((e) => ({{ ...e }}));
		let nextNodeId = allNodes.length ? Math.max(...allNodes.map((n) => n.id)) + 1 : 1;
		let nextEdgeId = allEdges.length ? Math.max(...allEdges.map((e) => e.id || 0)) + 1 : 1;

		const nodes = new vis.DataSet([]);
		const edges = new vis.DataSet([]);
		const container = document.getElementById("graph");
		const data = {{ nodes, edges }};

		const searchInput = document.getElementById("searchInput");
		const searchInfo = document.getElementById("searchInfo");
		const metaStats = document.getElementById("metaStats");
		const nodeNameList = document.getElementById("nodeNameList");
		const pageComponentSelect = document.getElementById("pageComponentSelect");
		const pageInfo = document.getElementById("pageInfo");
		const prevPageBtn = document.getElementById("prevPageBtn");
		const nextPageBtn = document.getElementById("nextPageBtn");

		let componentVisibility = new Set();
		let currentKeyword = "";
		let pagedMode = true;
		let currentPageComponent = null;
		let focusNodeId = null;
		let focusEdgeId = null;

		const BASE_NODE_STYLE = {{
			background: "#3e8577",
			border: "#27534a",
			fontColor: "#102320",
		}};
		const BASE_EDGE_STYLE = {{
			line: "#5b7d76",
			highlight: "#c96f3f",
			fontColor: "#27453f",
		}};

		function normalize(s) {{
			return (s || "").trim().toLowerCase();
		}}

		function hexToRgb(hex) {{
			const safe = (hex || "").replace("#", "").trim();
			if (safe.length !== 6) {{
				return [0, 0, 0];
			}}
			return [
				parseInt(safe.slice(0, 2), 16),
				parseInt(safe.slice(2, 4), 16),
				parseInt(safe.slice(4, 6), 16),
			];
		}}

		function rgba(hex, alpha) {{
			const [r, g, b] = hexToRgb(hex);
			return `rgba(${{r}}, ${{g}}, ${{b}}, ${{alpha}})`;
		}}

		function resetFocusStyles() {{
			const nodeUpdates = nodes.get().map((node) => ({{
				id: node.id,
				size: 13,
				color: {{
					background: BASE_NODE_STYLE.background,
					border: BASE_NODE_STYLE.border,
					highlight: {{ background: "#f39b6d", border: "#a14c24" }},
				}},
				font: {{ color: BASE_NODE_STYLE.fontColor, size: 14, face: "Microsoft YaHei" }},
			}}));

			const edgeUpdates = edges.get().map((edge) => ({{
				id: edge.id,
				color: {{ color: BASE_EDGE_STYLE.line, highlight: BASE_EDGE_STYLE.highlight }},
				font: {{ color: BASE_EDGE_STYLE.fontColor, size: 12, strokeWidth: 0, align: "middle", face: "Microsoft YaHei" }},
			}}));

			nodes.update(nodeUpdates);
			edges.update(edgeUpdates);
		}}

		function applyFocusHighlight(selectedId) {{
			if (!selectedId || !nodes.get(selectedId)) {{
				resetFocusStyles();
				return;
			}}

			const adjacency = new Map();
			nodes.getIds().forEach((id) => adjacency.set(id, new Set()));
			edges.get().forEach((edge) => {{
				if (adjacency.has(edge.from) && adjacency.has(edge.to)) {{
					adjacency.get(edge.from).add(edge.to);
					adjacency.get(edge.to).add(edge.from);
				}}
			}});

			const keepNodes = new Set([selectedId]);
			(adjacency.get(selectedId) || new Set()).forEach((nb) => keepNodes.add(nb));

			const nodeUpdates = nodes.get().map((node) => {{
				const isSelected = node.id === selectedId;
				const keep = keepNodes.has(node.id);
				if (isSelected) {{
					return {{
						id: node.id,
						size: 16,
						color: {{
							background: "#f39b6d",
							border: "#a14c24",
							highlight: {{ background: "#f39b6d", border: "#a14c24" }},
						}},
						font: {{ color: "#102320", size: 15, face: "Microsoft YaHei" }},
					}};
				}}
				if (keep) {{
					return {{
						id: node.id,
						size: 13,
						color: {{
							background: BASE_NODE_STYLE.background,
							border: BASE_NODE_STYLE.border,
							highlight: {{ background: "#f39b6d", border: "#a14c24" }},
						}},
						font: {{ color: BASE_NODE_STYLE.fontColor, size: 14, face: "Microsoft YaHei" }},
					}};
				}}
				return {{
					id: node.id,
					size: 12,
					color: {{
						background: rgba(BASE_NODE_STYLE.background, 0.18),
						border: rgba(BASE_NODE_STYLE.border, 0.2),
						highlight: {{
							background: rgba(BASE_NODE_STYLE.background, 0.3),
							border: rgba(BASE_NODE_STYLE.border, 0.3),
						}},
					}},
					font: {{ color: rgba(BASE_NODE_STYLE.fontColor, 0.34), size: 13, face: "Microsoft YaHei" }},
				}};
			}});

			const edgeUpdates = edges.get().map((edge) => {{
				const connectedToSelected = edge.from === selectedId || edge.to === selectedId;
				if (connectedToSelected) {{
					return {{
						id: edge.id,
						color: {{ color: BASE_EDGE_STYLE.line, highlight: BASE_EDGE_STYLE.highlight }},
						font: {{ color: BASE_EDGE_STYLE.fontColor, size: 12, strokeWidth: 0, align: "middle", face: "Microsoft YaHei" }},
					}};
				}}
				return {{
					id: edge.id,
					color: {{
						color: rgba(BASE_EDGE_STYLE.line, 0.14),
						highlight: rgba(BASE_EDGE_STYLE.line, 0.22),
					}},
					font: {{ color: rgba(BASE_EDGE_STYLE.fontColor, 0.25), size: 11, strokeWidth: 0, align: "middle", face: "Microsoft YaHei" }},
				}};
			}});

			nodes.update(nodeUpdates);
			edges.update(edgeUpdates);
		}}

		function applyEdgeFocusHighlight(selectedEdgeId) {{
			if (!selectedEdgeId || !edges.get(selectedEdgeId)) {{
				if (focusNodeId && nodes.get(focusNodeId)) {{
					applyFocusHighlight(focusNodeId);
				}} else {{
					resetFocusStyles();
				}}
				return;
			}}

			const selectedEdge = edges.get(selectedEdgeId);
			const keepNodes = new Set([selectedEdge.from, selectedEdge.to]);
			const nodeUpdates = nodes.get().map((node) => {{
				const keep = keepNodes.has(node.id);
				if (keep) {{
					return {{
						id: node.id,
						size: 15,
						color: {{
							background: "#f39b6d",
							border: "#a14c24",
							highlight: {{ background: "#f39b6d", border: "#a14c24" }},
						}},
						font: {{ color: "#102320", size: 14, face: "Microsoft YaHei" }},
					}};
				}}
				return {{
					id: node.id,
					size: 12,
					color: {{
						background: rgba(BASE_NODE_STYLE.background, 0.16),
						border: rgba(BASE_NODE_STYLE.border, 0.2),
						highlight: {{
							background: rgba(BASE_NODE_STYLE.background, 0.26),
							border: rgba(BASE_NODE_STYLE.border, 0.26),
						}},
					}},
					font: {{ color: rgba(BASE_NODE_STYLE.fontColor, 0.3), size: 13, face: "Microsoft YaHei" }},
				}};
			}});

			const edgeUpdates = edges.get().map((edge) => {{
				if (edge.id === selectedEdgeId) {{
					return {{
						id: edge.id,
						width: 2.8,
						color: {{ color: "#d36b3f", highlight: "#d36b3f" }},
						font: {{ color: "#213f39", size: 12, strokeWidth: 0, align: "middle", face: "Microsoft YaHei" }},
					}};
				}}
				return {{
					id: edge.id,
					width: 1,
					color: {{
						color: rgba(BASE_EDGE_STYLE.line, 0.12),
						highlight: rgba(BASE_EDGE_STYLE.line, 0.2),
					}},
					font: {{ color: rgba(BASE_EDGE_STYLE.fontColor, 0.22), size: 11, strokeWidth: 0, align: "middle", face: "Microsoft YaHei" }},
				}};
			}});

			nodes.update(nodeUpdates);
			edges.update(edgeUpdates);
			network.selectEdges([selectedEdgeId]);
		}}

		function getComponentIds() {{
			return [...new Set(allNodes.map((n) => n.component))].sort((a, b) => a - b);
		}}

		function refreshPageControls() {{
			const componentIds = getComponentIds();
			pageComponentSelect.innerHTML = "";

			componentIds.forEach((cid) => {{
				const option = document.createElement("option");
				option.value = String(cid);
				option.textContent = `图谱 ${{cid}}`;
				pageComponentSelect.appendChild(option);
			}});

			if (!componentIds.length) {{
				pageInfo.textContent = "暂无可展示分区";
				prevPageBtn.disabled = true;
				nextPageBtn.disabled = true;
				pageComponentSelect.disabled = true;
				return;
			}}

			if (!currentPageComponent || !componentIds.includes(currentPageComponent)) {{
				currentPageComponent = componentIds[0];
			}}

			const pageIndex = componentIds.indexOf(currentPageComponent);
			pageComponentSelect.value = String(currentPageComponent);
			pageComponentSelect.disabled = false;
			prevPageBtn.disabled = componentIds.length <= 1;
			nextPageBtn.disabled = componentIds.length <= 1;

			if (pagedMode) {{
				pageInfo.textContent = `第 ${{pageIndex + 1}} / ${{componentIds.length}} 页，仅显示图谱 ${{currentPageComponent}}`;
			}} else {{
				pageInfo.textContent = `总览模式：显示 ${{componentIds.length}} 个分区`;
			}}
		}}

		function jumpToPageComponent(targetComponent) {{
			const componentIds = getComponentIds();
			if (!componentIds.includes(targetComponent)) {{
				return;
			}}
			currentPageComponent = targetComponent;
			if (pagedMode) {{
				componentVisibility = new Set([currentPageComponent]);
			}}
			applyFilters();
			refreshPageControls();
			network.fit({{ animation: true }});
		}}

		function getActiveComponentForInsert() {{
			const componentIds = getComponentIds();
			if (!componentIds.length) {{
				return 1;
			}}
			if (pagedMode && currentPageComponent && componentIds.includes(currentPageComponent)) {{
				return currentPageComponent;
			}}
			const visibleComponents = [...componentVisibility].filter((cid) => componentIds.includes(cid));
			if (visibleComponents.length) {{
				return visibleComponents[0];
			}}
			return componentIds[0];
		}}

		function findBlankPositionForNewNode(componentId) {{
			const center = network.getViewPosition();
			const visibleNodes = nodes
				.get()
				.filter((n) => n.component === componentId)
				.map((n) => ({{ x: n.x || 0, y: n.y || 0 }}));

			if (!visibleNodes.length) {{
				return {{ x: center.x, y: center.y }};
			}}

			const minGap = 120;
			let bestPoint = {{ x: center.x, y: center.y }};
			let bestScore = -1;

			for (let ring = 0; ring < 14; ring += 1) {{
				const radius = 40 + ring * 50;
				const samples = 8 + ring * 4;
				for (let i = 0; i < samples; i += 1) {{
					const angle = (Math.PI * 2 * i) / samples;
					const candidate = {{
						x: center.x + Math.cos(angle) * radius,
						y: center.y + Math.sin(angle) * radius,
					}};

					let nearest = Number.POSITIVE_INFINITY;
					for (const p of visibleNodes) {{
						const dx = candidate.x - p.x;
						const dy = candidate.y - p.y;
						const dist = Math.hypot(dx, dy);
						nearest = Math.min(nearest, dist);
					}}

					if (nearest >= minGap) {{
						return candidate;
					}}
					if (nearest > bestScore) {{
						bestScore = nearest;
						bestPoint = candidate;
					}}
				}}
			}}

			return bestPoint;
		}}

		function rebuildComponents() {{
			const adjacency = new Map();
			allNodes.forEach((n) => adjacency.set(n.id, new Set()));
			allEdges.forEach((e) => {{
				if (adjacency.has(e.from) && adjacency.has(e.to)) {{
					adjacency.get(e.from).add(e.to);
					adjacency.get(e.to).add(e.from);
				}}
			}});

			const visited = new Set();
			let componentId = 0;
			for (const n of allNodes) {{
				if (visited.has(n.id)) {{
					continue;
				}}
				componentId += 1;
				const queue = [n.id];
				visited.add(n.id);
				while (queue.length) {{
					const cur = queue.shift();
					const node = allNodes.find((item) => item.id === cur);
					if (node) {{
						node.component = componentId;
					}}
					(adjacency.get(cur) || new Set()).forEach((nb) => {{
						if (!visited.has(nb)) {{
							visited.add(nb);
							queue.push(nb);
						}}
					}});
				}}
			}}

			allEdges = allEdges.map((e) => {{
				const fromNode = allNodes.find((n) => n.id === e.from);
				return {{ ...e, component: fromNode ? fromNode.component : 1 }};
			}});

			const allComponentIds = getComponentIds();
			if (pagedMode) {{
				if (!allComponentIds.length) {{
					currentPageComponent = null;
					componentVisibility = new Set();
				}} else {{
					if (!currentPageComponent || !allComponentIds.includes(currentPageComponent)) {{
						currentPageComponent = allComponentIds[0];
					}}
					componentVisibility = new Set([currentPageComponent]);
				}}
			}} else {{
				componentVisibility = new Set(allComponentIds);
			}}
		}}

		function partitionLayout() {{
			const byComponent = new Map();
			allNodes.forEach((n) => {{
				if (!byComponent.has(n.component)) {{
					byComponent.set(n.component, []);
				}}
				byComponent.get(n.component).push(n);
			}});

			const componentIds = [...byComponent.keys()].sort((a, b) => a - b);
			const cols = Math.max(1, Math.ceil(Math.sqrt(componentIds.length)));
			const maxGroupSize = componentIds.reduce((maxSize, cid) => {{
				const size = (byComponent.get(cid) || []).length;
				return Math.max(maxSize, size);
			}}, 1);
			const densityScale = Math.min(2.5, Math.max(1.1, Math.sqrt(maxGroupSize / 20)));
			const cellW = Math.round(860 * densityScale);
			const cellH = Math.round(660 * densityScale);

			componentIds.forEach((cid, index) => {{
				const group = byComponent.get(cid) || [];
				const col = index % cols;
				const row = Math.floor(index / cols);
				const centerX = col * cellW + cellW / 2;
				const centerY = row * cellH + cellH / 2;

				let ringIndex = 0;
				let indexInRing = 0;
				let ringCapacity = 8;

				group.forEach((node) => {{
					if (indexInRing >= ringCapacity) {{
						ringIndex += 1;
						indexInRing = 0;
						ringCapacity = 8 + ringIndex * 5;
					}}

					const baseRadius = 92 + ringIndex * 126;
					const angle = (Math.PI * 2 * indexInRing) / Math.max(1, ringCapacity) + (ringIndex % 2) * 0.22;
					const seed = (node.id * 1103515245 + cid * 12345) & 0x7fffffff;
					const radialJitter = (seed % 29) - 14;
					const tangentialJitter = ((Math.floor(seed / 19) % 13) - 6) * 0.015;

					node.x = centerX + Math.cos(angle + tangentialJitter) * (baseRadius + radialJitter);
					node.y = centerY + Math.sin(angle + tangentialJitter) * (baseRadius + radialJitter);

					indexInRing += 1;
				}});
			}});
		}}

		function applyFilters() {{
			const keyword = normalize(currentKeyword);
			const componentAllowed = new Set(componentVisibility);

			let visibleNodeIds = new Set();
			let visibleEdgeIds = new Set();

			const componentNodes = allNodes.filter((n) => componentAllowed.has(n.component));
			const componentNodeIdSet = new Set(componentNodes.map((n) => n.id));

			if (!keyword) {{
				componentNodes.forEach((n) => visibleNodeIds.add(n.id));
				allEdges.forEach((e) => {{
					if (componentAllowed.has(e.component) && componentNodeIdSet.has(e.from) && componentNodeIdSet.has(e.to)) {{
						visibleEdgeIds.add(e.id);
					}}
				}});
				searchInfo.textContent = "当前未启用搜索过滤";
			}} else {{
				const matched = componentNodes.filter((n) => normalize(n.label).includes(keyword));
				const matchedSet = new Set(matched.map((n) => n.id));

				allEdges.forEach((e) => {{
					if (!componentAllowed.has(e.component)) {{
						return;
					}}
					const hit = matchedSet.has(e.from) || matchedSet.has(e.to);
					if (hit) {{
						visibleEdgeIds.add(e.id);
						if (componentNodeIdSet.has(e.from)) {{
							visibleNodeIds.add(e.from);
						}}
						if (componentNodeIdSet.has(e.to)) {{
							visibleNodeIds.add(e.to);
						}}
					}}
				}});

				matched.forEach((n) => visibleNodeIds.add(n.id));
				searchInfo.textContent = `匹配节点 ${{matched.length}} 个，显示其相关关系。`;
			}}

			nodes.clear();
			edges.clear();
			nodes.add(allNodes.filter((n) => visibleNodeIds.has(n.id)));
			edges.add(allEdges.filter((e) => visibleEdgeIds.has(e.id)));

			metaStats.textContent = `节点数: ${{allNodes.length}} | 关系数: ${{allEdges.length}} | 图谱分区: ${{new Set(allNodes.map((n) => n.component)).size}} | 当前显示节点: ${{nodes.length}}`;

			if (focusNodeId && visibleNodeIds.has(focusNodeId)) {{
				applyFocusHighlight(focusNodeId);
			}} else {{
				focusNodeId = null;
				applyFocusHighlight(null);
			}}

			if (focusEdgeId && visibleEdgeIds.has(focusEdgeId)) {{
				applyEdgeFocusHighlight(focusEdgeId);
			}} else {{
				focusEdgeId = null;
				applyEdgeFocusHighlight(null);
			}}
		}}

		function refreshNodeNameList() {{
			nodeNameList.innerHTML = "";
			allNodes
				.slice()
				.sort((a, b) => a.label.localeCompare(b.label, "zh-CN"))
				.forEach((n) => {{
					const option = document.createElement("option");
					option.value = n.label;
					nodeNameList.appendChild(option);
				}});
		}}

		function downloadText(filename, content, mime) {{
			const blob = new Blob([content], {{ type: mime }});
			const url = URL.createObjectURL(blob);
			const a = document.createElement("a");
			a.href = url;
			a.download = filename;
			document.body.appendChild(a);
			a.click();
			a.remove();
			URL.revokeObjectURL(url);
		}}

		function showGraphError(err) {{
			const message = err && err.message ? err.message : String(err);
			const graph = document.getElementById("graph");
			graph.innerHTML = `<div class="graph-error">图谱初始化失败：${{message}}<br/>请刷新页面或将报错信息反馈给开发者。</div>`;
		}}

		const options = {{
			layout: {{
				improvedLayout: true
			}},
			physics: {{
				enabled: false
			}},
			nodes: {{
				shape: "dot",
				size: 13,
				color: {{
					background: "#3e8577",
					border: "#27534a",
					highlight: {{ background: "#f39b6d", border: "#a14c24" }}
				}},
				font: {{
					color: "#102320",
					size: 14,
					face: "Microsoft YaHei"
				}}
			}},
			edges: {{
				arrows: {{ to: {{ enabled: false }} }},
				smooth: {{ type: "continuous" }},
				color: {{ color: "#5b7d76", highlight: "#c96f3f" }},
				font: {{
					color: "#27453f",
					size: 12,
					strokeWidth: 0,
					align: "middle",
					face: "Microsoft YaHei"
				}}
			}},
			interaction: {{
				hover: true,
				tooltipDelay: 120,
				navigationButtons: true,
				keyboard: true
			}}
		}};

		const network = new vis.Network(container, data, options);
		nodes.add(allNodes);
		edges.add(allEdges);

		network.on("selectNode", (params) => {{
			focusEdgeId = null;
			focusNodeId = params.nodes && params.nodes.length ? params.nodes[0] : null;
			applyFocusHighlight(focusNodeId);
		}});

		network.on("deselectNode", () => {{
			focusNodeId = null;
			applyFocusHighlight(null);
		}});

		network.on("selectEdge", (params) => {{
			focusNodeId = null;
			const edgeId = params.edges && params.edges.length ? params.edges[0] : null;
			focusEdgeId = edgeId;
			applyFocusHighlight(null);
			applyEdgeFocusHighlight(edgeId);
		}});

		network.on("deselectEdge", () => {{
			focusEdgeId = null;
			applyEdgeFocusHighlight(null);
		}});

		network.on("click", (params) => {{
			if (!params.nodes || !params.nodes.length) {{
				focusNodeId = null;
				applyFocusHighlight(null);
			}}
			if (!params.edges || !params.edges.length) {{
				focusEdgeId = null;
				applyEdgeFocusHighlight(null);
			}}
		}});

		document.getElementById("searchBtn").addEventListener("click", () => {{
			currentKeyword = searchInput.value;
			applyFilters();
			network.fit({{ animation: true }});
		}});

		document.getElementById("clearSearchBtn").addEventListener("click", () => {{
			searchInput.value = "";
			currentKeyword = "";
			applyFilters();
		}});

		document.getElementById("enablePagedMode").addEventListener("click", () => {{
			pagedMode = true;
			const componentIds = getComponentIds();
			if (!currentPageComponent || !componentIds.includes(currentPageComponent)) {{
				currentPageComponent = componentIds[0] || null;
			}}
			componentVisibility = currentPageComponent ? new Set([currentPageComponent]) : new Set();
			applyFilters();
			refreshPageControls();
			network.fit({{ animation: true }});
		}});

		document.getElementById("enableOverviewMode").addEventListener("click", () => {{
			pagedMode = false;
			componentVisibility = new Set(getComponentIds());
			applyFilters();
			refreshPageControls();
			network.fit({{ animation: true }});
		}});

		pageComponentSelect.addEventListener("change", () => {{
			const target = Number(pageComponentSelect.value);
			if (!Number.isNaN(target)) {{
				jumpToPageComponent(target);
			}}
		}});

		prevPageBtn.addEventListener("click", () => {{
			const componentIds = getComponentIds();
			if (!componentIds.length) {{
				return;
			}}
			const curIndex = Math.max(0, componentIds.indexOf(currentPageComponent));
			const nextIndex = (curIndex - 1 + componentIds.length) % componentIds.length;
			jumpToPageComponent(componentIds[nextIndex]);
		}});

		nextPageBtn.addEventListener("click", () => {{
			const componentIds = getComponentIds();
			if (!componentIds.length) {{
				return;
			}}
			const curIndex = Math.max(0, componentIds.indexOf(currentPageComponent));
			const nextIndex = (curIndex + 1) % componentIds.length;
			jumpToPageComponent(componentIds[nextIndex]);
		}});

		document.getElementById("addNodeBtn").addEventListener("click", () => {{
			const labelInput = document.getElementById("newNodeLabel");
			const descInput = document.getElementById("newNodeDesc");
			const label = (labelInput.value || "").trim();
			const desc = (descInput.value || "").trim();
			if (!label) {{
				alert("节点名称不能为空。");
				return;
			}}
			const existed = allNodes.find((n) => normalize(n.label) === normalize(label));
			if (existed) {{
				alert("已存在同名节点，请更换名称。");
				return;
			}}

			const targetComponent = getActiveComponentForInsert();
			const pos = findBlankPositionForNewNode(targetComponent);
			const newNodeId = nextNodeId++;

			allNodes.push({{
				id: newNodeId,
				label,
				title: desc || label,
				component: targetComponent,
				x: pos.x,
				y: pos.y,
			}});

			if (pagedMode) {{
				currentPageComponent = targetComponent;
				componentVisibility = new Set([targetComponent]);
			}} else {{
				componentVisibility.add(targetComponent);
			}}
			refreshPageControls();
			refreshNodeNameList();
			applyFilters();

			focusNodeId = newNodeId;
			network.selectNodes([newNodeId]);
			network.focus(newNodeId, {{ scale: 1.05, animation: {{ duration: 280, easingFunction: "easeInOutQuad" }} }});
			applyFocusHighlight(newNodeId);

			labelInput.value = "";
			descInput.value = "";
		}});

		document.getElementById("addRelationBtn").addEventListener("click", () => {{
			const sourceName = (document.getElementById("relSource").value || "").trim();
			const targetName = (document.getElementById("relTarget").value || "").trim();
			const relationLabel = (document.getElementById("relLabel").value || "").trim();
			const direction = document.getElementById("relDirection").value;
			if (!sourceName || !targetName || !relationLabel) {{
				alert("请完整填写起点、终点和关系名称。");
				return;
			}}

			const srcNode = allNodes.find((n) => n.label === sourceName);
			const dstNode = allNodes.find((n) => n.label === targetName);
			if (!srcNode || !dstNode) {{
				alert("起点或终点节点不存在，请先创建节点或从候选中选择。");
				return;
			}}

			const directed = direction === "directed";
			const duplicate = allEdges.some((e) => {{
				if (e.label !== relationLabel || !!e.directed !== directed) {{
					return false;
				}}
				if (directed) {{
					return e.from === srcNode.id && e.to === dstNode.id;
				}}
				return (
					(e.from === srcNode.id && e.to === dstNode.id) ||
					(e.from === dstNode.id && e.to === srcNode.id)
				);
			}});

			if (duplicate) {{
				alert("该关系已存在，未重复创建。");
				return;
			}}

			const newEdgeId = nextEdgeId++;
			allEdges.push({{
				id: newEdgeId,
				from: srcNode.id,
				to: dstNode.id,
				label: relationLabel,
					title: directed
						? `${{sourceName}} --${{relationLabel}}--> ${{targetName}}`
						: `${{sourceName}} --${{relationLabel}}-- ${{targetName}}`,
				directed,
					arrows: directed
						? {{ to: {{ enabled: true, scaleFactor: 0.7 }} }}
						: {{ to: {{ enabled: false }} }},
			}});

			rebuildComponents();
			partitionLayout();
			const insertedEdge = allEdges.find((e) => e.id === newEdgeId);
			if (insertedEdge) {{
				currentPageComponent = insertedEdge.component;
				if (pagedMode) {{
					componentVisibility = new Set([insertedEdge.component]);
				}} else {{
					componentVisibility.add(insertedEdge.component);
				}}
			}}
			refreshPageControls();
			focusNodeId = null;
			applyFilters();

			focusEdgeId = newEdgeId;
			network.unselectAll();
			network.selectEdges([newEdgeId]);
			applyEdgeFocusHighlight(newEdgeId);
			const fromNodePos = allNodes.find((n) => n.id === srcNode.id);
			const toNodePos = allNodes.find((n) => n.id === dstNode.id);
			if (fromNodePos && toNodePos) {{
				network.moveTo({{
					position: {{
						x: ((fromNodePos.x || 0) + (toNodePos.x || 0)) / 2,
						y: ((fromNodePos.y || 0) + (toNodePos.y || 0)) / 2,
					}},
					scale: 1.05,
					animation: {{ duration: 300, easingFunction: "easeInOutQuad" }},
				}});
			}} else {{
				network.fit({{ animation: true }});
			}}

			document.getElementById("relLabel").value = "";
		}});

		document.getElementById("exportJsonBtn").addEventListener("click", () => {{
			const payload = {{
				title: document.title,
				nodes: allNodes,
				edges: allEdges,
			}};
			downloadText("knowledge_graph_snapshot.json", JSON.stringify(payload, null, 2), "application/json;charset=utf-8");
		}});

		document.getElementById("exportCsvBtn").addEventListener("click", () => {{
			const idToLabel = new Map(allNodes.map((n) => [n.id, n.label]));
			const rows = ["节点A,关系,节点B,方向"];
			allEdges.forEach((e) => {{
				const a = idToLabel.get(e.from) || "";
				const b = idToLabel.get(e.to) || "";
				const direction = e.directed ? "有向" : "无向";
				rows.push(`${{a}},${{e.label}},${{b}},${{direction}}`);
			}});
			downloadText("knowledge_graph_snapshot.csv", rows.join("\\n"), "text/csv;charset=utf-8");
		}});

		try {{
			rebuildComponents();
			partitionLayout();
			refreshPageControls();
			refreshNodeNameList();
			applyFilters();
			network.fit({{ animation: true }});
		}} catch (err) {{
			console.error(err);
			showGraphError(err);
		}}
	</script>
</body>
</html>
"""


VIS_BUNDLE_URLS = [
	"https://cdn.jsdelivr.net/npm/vis-network@9.1.2/standalone/umd/vis-network.min.js",
	"https://unpkg.com/vis-network@9.1.2/standalone/umd/vis-network.min.js",
]


def _prepare_vis_script_tags(output_html: Path) -> str:
	"""Generate script tags for vis-network.

	Priority:
	1. Try local bundle first (download and cache if missing).
	2. Keep CDN fallbacks to improve runtime resilience.
	"""
	local_bundle = output_html.parent / "vis-network.min.js"

	if not local_bundle.exists():
		for url in VIS_BUNDLE_URLS:
			try:
				with urlopen(url, timeout=12) as resp:
					content = resp.read()
				if content:
					local_bundle.write_bytes(content)
					break
			except (URLError, TimeoutError, OSError):
				continue

	tags: list[str] = []
	if local_bundle.exists():
		rel = Path(os.path.relpath(local_bundle, output_html.parent)).as_posix()
		tags.append(f'<script type="text/javascript" src="{rel}"></script>')

	for url in VIS_BUNDLE_URLS:
		tags.append(f'<script type="text/javascript" src="{url}"></script>')

	return "\n\t".join(tags)


def _read_triples(csv_path: Path) -> list[tuple[str, str, str]]:
	"""Read triples from CSV.

	Preferred headers are `节点A`, `关系`, `节点B`.
	If headers are missing, fallback to the first 3 columns.
	"""
	triples: list[tuple[str, str, str]] = []
	with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
		reader = csv.DictReader(f)
		if reader.fieldnames is None:
			raise ValueError("CSV文件为空或缺少表头。")

		normalized_headers = {name.strip(): name for name in reader.fieldnames}
		src_key = normalized_headers.get("节点A")
		rel_key = normalized_headers.get("关系")
		dst_key = normalized_headers.get("节点B")

		for row in reader:
			if src_key and rel_key and dst_key:
				source = (row.get(src_key) or "").strip()
				relation = (row.get(rel_key) or "").strip()
				target = (row.get(dst_key) or "").strip()
			else:
				values = [str(v).strip() for v in row.values()]
				if len(values) < 3:
					continue
				source, relation, target = values[0], values[1], values[2]

			if source and relation and target:
				triples.append((source, relation, target))

	return triples


def _assign_components(nodes: list[dict], edges: list[dict]) -> int:
	"""Compute connected components for nodes and edges in-place."""
	adjacency: dict[int, set[int]] = {node["id"]: set() for node in nodes}
	for edge in edges:
		adjacency[edge["from"]].add(edge["to"])
		adjacency[edge["to"]].add(edge["from"])

	component_map: dict[int, int] = {}
	component_id = 0

	for node in nodes:
		nid = node["id"]
		if nid in component_map:
			continue

		component_id += 1
		stack = [nid]
		component_map[nid] = component_id

		while stack:
			cur = stack.pop()
			for nb in adjacency[cur]:
				if nb not in component_map:
					component_map[nb] = component_id
					stack.append(nb)

	for node in nodes:
		node["component"] = component_map[node["id"]]

	for edge in edges:
		edge["component"] = component_map[edge["from"]]

	return component_id


def _build_vis_data(triples: list[tuple[str, str, str]]) -> tuple[list[dict], list[dict], int]:
	"""Convert triples into vis-network nodes/edges and assign component IDs."""
	node_ids: dict[str, int] = {}
	nodes: list[dict] = []
	edges: list[dict] = []
	seen_edges: set[tuple[str, str, str]] = set()

	def ensure_node_id(name: str) -> int:
		if name not in node_ids:
			node_ids[name] = len(node_ids) + 1
			nodes.append({"id": node_ids[name], "label": name, "title": name})
		return node_ids[name]

	for source, relation, target in triples:
		edge_key = (source, relation, target)
		if edge_key in seen_edges:
			continue
		seen_edges.add(edge_key)

		src_id = ensure_node_id(source)
		dst_id = ensure_node_id(target)
		edges.append(
			{
				"id": len(edges) + 1,
				"from": src_id,
				"to": dst_id,
				"label": relation,
				"title": f"{source} --{relation}--> {target}",
				"directed": True,
				"arrows": {"to": {"enabled": True, "scaleFactor": 0.7}},
			}
		)

	component_count = _assign_components(nodes, edges)
	return nodes, edges, component_count


def generate_kg_html(csv_path: Path, output_html: Path, title: str) -> tuple[int, int]:
	"""Build interactive HTML from CSV triples and return (node_count, edge_count)."""
	triples = _read_triples(csv_path)
	if not triples:
		raise ValueError("没有读取到有效三元组，请检查CSV内容。")

	vis_script_tags = _prepare_vis_script_tags(output_html)
	nodes, edges, component_count = _build_vis_data(triples)

	html = HTML_TEMPLATE.format(
		title=title,
		vis_script_tags=vis_script_tags,
		node_count=len(nodes),
		edge_count=len(edges),
		component_count=component_count,
		nodes=json.dumps(nodes, ensure_ascii=False),
		edges=json.dumps(edges, ensure_ascii=False),
	)

	output_html.write_text(html, encoding="utf-8")
	return len(nodes), len(edges)


def main() -> None:
	base_dir = Path(__file__).resolve().parent
	workspace_dir = base_dir.parent
	parser = argparse.ArgumentParser(description="根据CSV三元组构建知识图谱并导出交互式HTML")
	parser.add_argument(
		"--csv",
		type=Path,
		default=base_dir / "Stage_Tech_MindSet.csv",
		help="输入CSV文件路径，默认读取当前目录下 Stage_Tech_MindSet.csv",
	)
	parser.add_argument(
		"--out",
		type=Path,
		default=base_dir / "knowledge_graph_interactive.html",
		help="输出HTML文件路径",
	)
	parser.add_argument(
		"--title",
		type=str,
		default="CSV知识图谱可视化",
		help="图谱标题",
	)
	parser.add_argument(
		"--publish-site",
		action="store_true",
		help="一键发布到工作区 site/index.html（会覆盖该文件）",
	)
	args = parser.parse_args()

	csv_path = args.csv if args.csv.is_absolute() else (base_dir / args.csv)
	out_path = args.out if args.out.is_absolute() else (base_dir / args.out)

	if args.publish_site:
		out_path = workspace_dir / "site" / "index.html"

	if not csv_path.exists():
		raise FileNotFoundError(f"未找到CSV文件: {csv_path}")

	out_path.parent.mkdir(parents=True, exist_ok=True)
	node_count, edge_count = generate_kg_html(csv_path, out_path, args.title)
	print(f"构建完成: 节点 {node_count} 个, 关系 {edge_count} 条")
	print(f"输出文件: {out_path}")
	if args.publish_site:
		print("已发布到 site 目录，可直接用于静态网站托管。")


if __name__ == "__main__":
	main()
