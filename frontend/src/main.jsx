import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  AlertTriangle,
  BarChart3,
  Bell,
  Bot,
  Boxes,
  Building2,
  CalendarDays,
  ChevronRight,
  CircleDollarSign,
  ClipboardList,
  Database,
  Factory,
  Filter,
  Gauge,
  Home,
  LineChart as LineChartIcon,
  MapPinned,
  PackageCheck,
  RefreshCw,
  Route,
  Settings,
  ShieldAlert,
  SlidersHorizontal,
  Sparkles,
  Truck,
  UserRoundCheck,
  Warehouse,
} from "lucide-react";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ComposedChart,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { CircleMarker, MapContainer, Polyline, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import exlLogo from "./assets/exl_service_logo.svg";
import "./styles.css";

const COLORS = ["#0b63ce", "#41a05d", "#f2a91b", "#e5483f", "#6d5bd0", "#0798a6"];

const pages = [
  ["Executive Overview", Home, "/api/overview"],
  ["Demand Planning", LineChartIcon, "/api/demand"],
  ["Supply Planning", Factory, "/api/suppliers"],
  ["Inventory Planning", Boxes, "/api/inventory"],
  ["Warehouse / WMS Events", Warehouse, "/api/wms-events"],
  ["Transportation Planning", Truck, "/api/transport-cost"],
  ["Route Optimization", Route, "/api/routes"],
  ["Shipment Visibility", MapPinned, "/api/shipments"],
  ["Supplier & Carrier Performance", Building2, "/api/suppliers"],
  ["Engineer Parts Availability", UserRoundCheck, "/api/engineer-parts"],
  ["SLA Risk & Exceptions", ShieldAlert, "/api/sla-risk"],
  ["AI Agent Command Centre", Bot, "/api/ai-recommendations"],
  ["Scenario Simulation", SlidersHorizontal, null],
  ["Analytics & Reports", BarChart3, "/api/overview"],
  ["Data Management", Database, "/api/data-management"],
  ["Settings", Settings, null],
];

const filters = {
  region: ["UK", "Scotland", "Wales", "London", "Midlands", "North", "South"],
  depot: ["All Depots", "D-LON", "D-MID", "D-NTH", "D-SCO", "D-WAL", "D-STH"],
  warehouse: ["All Warehouses", "W-COV", "W-MAN", "W-GLA", "W-LON"],
  businessUnit: ["All", "Utility Field Services", "Smart Metering", "Energy Services"],
  jobType: ["All", "Repair", "Service", "Install", "Emergency", "Smart Meter Exchange"],
  scenario: ["Baseline", "Optimized", "Peak Demand", "Weather Disruption"],
  carrier: ["All Carriers", "C-001", "C-002", "C-003", "C-004", "C-005", "C-006"],
  supplier: ["All Suppliers", "S-001", "S-002", "S-003", "S-004", "S-005", "S-014"],
  engineerSkill: ["All Skills", "Gas Safe", "Boiler", "Smart Meter", "Electrical", "EV Charger"],
};

async function getJson(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`${url} failed with ${response.status}`);
  return response.json();
}

async function postJson(url, payload) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw new Error(`${url} failed with ${response.status}`);
  return response.json();
}

function Sidebar({ activePage, setActivePage }) {
  return (
    <aside className="sidebar">
      <div className="brand-row">
        <div className="logo-box">
          <img src={exlLogo} alt="EXL" />
        </div>
        <div>
          <strong>Logistics Planning</strong>
          <span>Control Tower</span>
        </div>
      </div>
      <nav className="side-nav">
        {pages.map(([label, Icon]) => (
          <button className={label === activePage ? "active" : ""} key={label} onClick={() => setActivePage(label)} type="button">
            <Icon size={18} />
            <span>{label}</span>
          </button>
        ))}
      </nav>
      <section className="quick-actions">
        <strong>Quick actions</strong>
        {["Create New Plan", "Run Simulation", "What-if Analysis", "Upload Data"].map((item) => (
          <button key={item} type="button">
            <span>{item}</span>
            <span>+</span>
          </button>
        ))}
      </section>
    </aside>
  );
}

function TopFilters() {
  return (
    <header className="topbar">
      <div className="date-filter">
        <CalendarDays size={17} />
        <span>Jun 01 - Jun 21, 2026</span>
      </div>
      {Object.entries(filters).map(([key, values]) => (
        <label className="filter-control" key={key}>
          <span>{key.replace(/([A-Z])/g, " $1")}</span>
          <select>
            {values.map((value) => (
              <option key={value}>{value}</option>
            ))}
          </select>
        </label>
      ))}
      <button className="icon-button" type="button" aria-label="Refresh">
        <RefreshCw size={18} />
      </button>
      <button className="icon-button alert-dot" type="button" aria-label="Alerts">
        <Bell size={18} />
      </button>
    </header>
  );
}

function KpiCard({ kpi, index }) {
  const icons = [Truck, PackageCheck, ClipboardList, Gauge, ShieldAlert, CircleDollarSign];
  const Icon = icons[index % icons.length];
  return (
    <article className="kpi-card">
      <div className="kpi-icon">
        <Icon size={24} />
      </div>
      <div>
        <span>{kpi.label}</span>
        <strong>{kpi.value}</strong>
        <small className={kpi.tone === "bad" ? "bad" : "good"}>
          {kpi.delta > 0 ? "+" : ""}
          {kpi.delta}% vs last period
        </small>
      </div>
    </article>
  );
}

function Panel({ title, subtitle, children, action }) {
  return (
    <section className="panel">
      <div className="panel-title">
        <div>
          <h2>{title}</h2>
          {subtitle && <p>{subtitle}</p>}
        </div>
        {action}
      </div>
      {children}
    </section>
  );
}

function Donut({ data, centerLabel }) {
  const safeData = data || [];
  return (
    <div className="donut-layout">
      <ResponsiveContainer width="48%" height={220}>
        <PieChart>
          <Pie data={safeData} dataKey="value" innerRadius={58} outerRadius={86} paddingAngle={2}>
            {safeData.map((_, index) => (
              <Cell fill={COLORS[index % COLORS.length]} key={index} />
            ))}
          </Pie>
          <Tooltip />
        </PieChart>
      </ResponsiveContainer>
      <div className="legend-list">
        <strong>{centerLabel}</strong>
        {safeData.map((item, index) => (
          <div key={item.name}>
            <i style={{ background: COLORS[index % COLORS.length] }} />
            <span>{item.name}</span>
            <b>{item.value}</b>
          </div>
        ))}
      </div>
    </div>
  );
}

function NetworkMap({ network }) {
  const safeNetwork = network || { nodes: [], routes: [] };
  const nodesById = Object.fromEntries(safeNetwork.nodes.map((node) => [node.id, node]));
  return (
    <MapContainer center={[53.2, -2.7]} zoom={5.3} scrollWheelZoom={false} className="leaflet-map" attributionControl={false}>
      {safeNetwork.routes.map(([from, to], index) => {
        const a = nodesById[from];
        const b = nodesById[to];
        if (!a || !b) return null;
        return <Polyline key={`${from}-${to}-${index}`} positions={[[a.lat, a.lng], [b.lat, b.lng]]} color={COLORS[index % COLORS.length]} weight={2} />;
      })}
      {safeNetwork.nodes.map((node) => (
        <CircleMarker
          center={[node.lat, node.lng]}
          fillColor={node.risk === "High" ? "#e5483f" : node.risk === "Medium" ? "#f2a91b" : "#0b63ce"}
          fillOpacity={0.9}
          key={node.id}
          radius={8}
          stroke
          weight={2}
        >
          <Popup>
            <strong>{node.name}</strong>
            <br />
            {node.type} - {node.risk} risk
          </Popup>
        </CircleMarker>
      ))}
    </MapContainer>
  );
}

function Recommendations({ items }) {
  const safeItems = items || [];
  return (
    <div className="recommendation-list">
      {safeItems.map((item) => (
        <article key={item}>
          <Sparkles size={17} />
          <span>{item}</span>
        </article>
      ))}
    </div>
  );
}

function OverviewPage({ data }) {
  const safeData = {
    kpis: [],
    demandForecast: [],
    inventoryPosition: [],
    shipmentStatus: [],
    transportCostTrend: [],
    network: { nodes: [], routes: [] },
    alerts: [],
    recommendations: [],
    improvements: [],
    ...data,
  };
  return (
    <>
      <section className="kpi-grid">
        {safeData.kpis.map((kpi, index) => (
          <KpiCard index={index} key={kpi.label} kpi={kpi} />
        ))}
      </section>

      <section className="dashboard-grid">
        <Panel title="Demand Forecast Overview" subtitle="Forecast vs actual">
          <ResponsiveContainer height={270} width="100%">
            <LineChart data={safeData.demandForecast}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line dataKey="forecast" stroke="#0b63ce" strokeWidth={3} />
              <Line dataKey="actual" stroke="#0b254f" strokeDasharray="5 5" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </Panel>
        <Panel title="Inventory Position">
          <Donut centerLabel="Inventory Risk" data={safeData.inventoryPosition} />
        </Panel>
        <Panel title="Shipment Status">
          <Donut centerLabel="Shipment Status" data={safeData.shipmentStatus} />
        </Panel>
        <Panel title="Transportation Cost Trend">
          <ResponsiveContainer height={240} width="100%">
            <AreaChart data={safeData.transportCostTrend}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Area dataKey="value" fill="#dcecff" stroke="#0b63ce" strokeWidth={3} />
            </AreaChart>
          </ResponsiveContainer>
        </Panel>
        <Panel title="UK Logistics Network Map" subtitle="Depots, warehouses, suppliers and routes">
          <NetworkMap network={safeData.network} />
        </Panel>
        <Panel title="Alerts & Exceptions" action={<button className="link-button">View All</button>}>
          <div className="alert-list">
            {safeData.alerts.map((alert) => (
              <div key={alert.type}>
                <AlertTriangle className={alert.severity === "High" ? "bad-text" : "warn-text"} size={18} />
                <span>{alert.type}</span>
                <b>{alert.count}</b>
                <ChevronRight size={16} />
              </div>
            ))}
          </div>
        </Panel>
      </section>

      <section className="wide-grid">
        <Panel title="AI Recommendation Panel">
          <Recommendations items={safeData.recommendations} />
        </Panel>
        <Panel title="Before vs After AI Optimization">
          <div className="improvement-grid">
            {safeData.improvements.map((item) => (
              <article key={item.metric}>
                <span>{item.metric}</span>
                <strong>
                  {item.before}
                  {item.unit === "%" ? "%" : ""} to {item.after}
                  {item.unit === "%" ? "%" : ""}
                </strong>
                <div>
                  <i style={{ width: `${Math.min(item.before, 100)}%` }} />
                  <b style={{ width: `${Math.min(item.after, 100)}%` }} />
                </div>
              </article>
            ))}
          </div>
        </Panel>
      </section>
    </>
  );
}

function DataTable({ rows, limit = 12 }) {
  if (!rows?.length) return <div className="empty-state">No rows available</div>;
  const columns = Object.keys(rows[0]).slice(0, 7);
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            {columns.map((column) => (
              <th key={column}>{column.replaceAll("_", " ")}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.slice(0, limit).map((row, rowIndex) => (
            <tr key={rowIndex}>
              {columns.map((column) => (
                <td key={column}>{String(row[column])}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function PlanningPage({ activePage, data }) {
  const rows = data.rows || data.topRows || data.riskRows || data.milestones || data.datasets || [];
  const chartData = data.byRegion || data.byJobType || data.status || data.eventTypes || data.matrix || data.riskMatrix || data.position || [];
  return (
    <>
      <section className="page-hero">
        <div>
          <p>{activePage}</p>
          <h2>{activePage} Control View</h2>
        </div>
        <Filter size={22} />
      </section>
      <section className="dashboard-grid">
        <Panel title={`${activePage} Distribution`}>
          <ResponsiveContainer height={280} width="100%">
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" fill="#0b63ce" radius={[6, 6, 0, 0]} />
              <Bar dataKey="count" fill="#0b63ce" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Panel>
        <Panel title="AI Recommendations">
          <Recommendations items={data.recommendations || []} />
        </Panel>
        <Panel title={`${activePage} Detail`} subtitle="Simulated operational dataset">
          <DataTable rows={rows} />
        </Panel>
      </section>
    </>
  );
}

function AgentCentre({ data }) {
  const safeData = {
    agents: [],
    recommendations: [],
    deliveryRisk: [],
    routeOptimization: [],
    inventoryRisk: [],
    supplierRisk: [],
    carrierAllocation: [],
    costOptimization: [],
    shipmentVisibility: [],
    engineerPartsAvailability: [],
    ...data,
  };
  const agentBlocks = [
    ["Delivery Risk", safeData.deliveryRisk],
    ["Route Optimization", safeData.routeOptimization],
    ["Inventory Risk", safeData.inventoryRisk],
    ["Supplier Risk", safeData.supplierRisk],
    ["Carrier Allocation", safeData.carrierAllocation],
    ["Cost Optimization", safeData.costOptimization],
    ["Shipment Visibility", safeData.shipmentVisibility],
    ["Engineer Parts Availability", safeData.engineerPartsAvailability],
  ];
  return (
    <>
      <section className="agent-grid">
        {safeData.agents.map((agent) => (
          <article className="agent-card" key={agent.name}>
            <Bot size={22} />
            <div>
              <h3>{agent.name}</h3>
              <span>{agent.status}</span>
              <p>{agent.impact}</p>
            </div>
          </article>
        ))}
      </section>
      <section className="wide-grid">
        <Panel title="AI Recommendation Panel">
          <Recommendations items={safeData.recommendations} />
        </Panel>
        <Panel title="Agent Outputs">
          <div className="agent-output-grid">
            {agentBlocks.map(([title, rows]) => (
              <article key={title}>
                <h3>{title}</h3>
                <DataTable limit={4} rows={rows} />
              </article>
            ))}
          </div>
        </Panel>
      </section>
    </>
  );
}

function ScenarioPage() {
  const [scenario, setScenario] = useState({
    demandIncrease: 20,
    fuelIncrease: 8,
    carrierCapacityReduction: 10,
    supplierDelay: 3,
    warehouseConstraint: 15,
    weatherDisruption: 35,
    depotStockout: 8,
    engineerAbsence: 5,
  });
  const [result, setResult] = useState(null);

  useEffect(() => {
    postJson("/api/scenario-simulation", scenario).then(setResult).catch(() => setResult(null));
  }, [scenario]);

  return (
    <section className="scenario-layout">
      <Panel title="Scenario Simulation" subtitle="Run what-if scenarios with Python-backed impact calculations">
        <div className="slider-grid">
          {Object.entries(scenario).map(([key, value]) => (
            <label key={key}>
              <span>
                {key.replace(/([A-Z])/g, " $1")} <b>{value}%</b>
              </span>
              <input
                max="60"
                min="0"
                onChange={(event) => setScenario((current) => ({ ...current, [key]: Number(event.target.value) }))}
                type="range"
                value={value}
              />
            </label>
          ))}
        </div>
      </Panel>
      {result && (
        <Panel title="Scenario Outputs">
          <ResponsiveContainer height={280} width="100%">
            <ComposedChart data={result.outputs}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="metric" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="baseline" fill="#a7c8f2" radius={[6, 6, 0, 0]} />
              <Bar dataKey="scenario" fill="#0b63ce" radius={[6, 6, 0, 0]} />
            </ComposedChart>
          </ResponsiveContainer>
          <Recommendations items={result.recommendations} />
        </Panel>
      )}
    </section>
  );
}

function SettingsPage() {
  return (
    <section className="settings-grid">
      {["API Connections", "Planning Rules", "Agent Thresholds", "User Roles", "Audit Controls", "Deployment"].map((item) => (
        <article className="settings-card" key={item}>
          <Settings size={20} />
          <strong>{item}</strong>
          <span>Configured for demo mode</span>
        </article>
      ))}
    </section>
  );
}

function App() {
  const [activePage, setActivePage] = useState("Executive Overview");
  const [pageData, setPageData] = useState(null);
  const [status, setStatus] = useState("loading");

  const endpoint = useMemo(() => pages.find(([label]) => label === activePage)?.[2], [activePage]);

  useEffect(() => {
    if (!endpoint) {
      setPageData(null);
      setStatus("ready");
      return;
    }
    setStatus("loading");
    getJson(endpoint)
      .then((data) => {
        setPageData(data);
        setStatus("ready");
      })
      .catch(() => setStatus("error"));
  }, [endpoint]);

  return (
    <div className="app-shell">
      <Sidebar activePage={activePage} setActivePage={setActivePage} />
      <main className="main-shell">
        <div className="page-header">
          <div>
            <h1>Logistics Planning Tool - {activePage}</h1>
            <p>UK utilities logistics control tower for depots, vans, parts, routes, suppliers, carriers and SLA performance.</p>
          </div>
          <button className="primary-button" type="button">
            <Sparkles size={18} />
            Optimize Plan
          </button>
        </div>
        <TopFilters />
        {status === "loading" && <div className="loading-card">Loading planning intelligence...</div>}
        {status === "error" && <div className="error-card">Flask API is not reachable. Start the backend service and refresh.</div>}
        {status === "ready" && activePage === "Executive Overview" && pageData && <OverviewPage data={pageData} />}
        {status === "ready" && activePage === "AI Agent Command Centre" && pageData && <AgentCentre data={pageData} />}
        {status === "ready" && activePage === "Scenario Simulation" && <ScenarioPage />}
        {status === "ready" && activePage === "Settings" && <SettingsPage />}
        {status === "ready" &&
          pageData &&
          !["Executive Overview", "AI Agent Command Centre", "Scenario Simulation", "Settings"].includes(activePage) && (
            <PlanningPage activePage={activePage} data={pageData} />
          )}
      </main>
    </div>
  );
}

createRoot(document.getElementById("root")).render(<App />);
