from flask import Flask, jsonify, request, send_from_directory

try:
    from agents import (
        all_agent_recommendations,
        carrier_allocation_agent,
        delivery_risk_agent,
        inventory_risk_agent,
        route_optimization_agent,
        scenario_simulation,
        supplier_risk_agent,
    )
    from data_service import (
        carriers,
        data_management,
        demand,
        engineer_parts,
        inventory,
        overview,
        routes,
        shipments,
        sla_risk,
        suppliers,
        transport_cost,
        wms_events,
    )
    from planner import build_plan
except ImportError:
    from backend.agents import (
        all_agent_recommendations,
        carrier_allocation_agent,
        delivery_risk_agent,
        inventory_risk_agent,
        route_optimization_agent,
        scenario_simulation,
        supplier_risk_agent,
    )
    from backend.data_service import (
        carriers,
        data_management,
        demand,
        engineer_parts,
        inventory,
        overview,
        routes,
        shipments,
        sla_risk,
        suppliers,
        transport_cost,
        wms_events,
    )
    from backend.planner import build_plan


def create_app() -> Flask:
    app = Flask(__name__, static_folder="../frontend/dist", static_url_path="")

    @app.post("/api/plan")
    def plan():
        return jsonify(build_plan(request.get_json(silent=True) or {}))

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok", "service": "utility-logistics-planner"})

    @app.get("/api/overview")
    def api_overview():
        return jsonify(overview())

    @app.get("/api/demand")
    def api_demand():
        return jsonify(demand())

    @app.get("/api/inventory")
    def api_inventory():
        return jsonify(inventory())

    @app.get("/api/shipments")
    def api_shipments():
        return jsonify(shipments())

    @app.get("/api/wms-events")
    def api_wms_events():
        return jsonify(wms_events())

    @app.get("/api/routes")
    def api_routes():
        return jsonify(routes())

    @app.get("/api/transport-cost")
    def api_transport_cost():
        return jsonify(transport_cost())

    @app.get("/api/suppliers")
    def api_suppliers():
        return jsonify(suppliers())

    @app.get("/api/carriers")
    def api_carriers():
        return jsonify(carriers())

    @app.get("/api/sla-risk")
    def api_sla_risk():
        return jsonify(sla_risk())

    @app.get("/api/engineer-parts")
    def api_engineer_parts():
        return jsonify(engineer_parts())

    @app.get("/api/ai-recommendations")
    def api_ai_recommendations():
        return jsonify(all_agent_recommendations())

    @app.post("/api/scenario-simulation")
    def api_scenario_simulation():
        return jsonify(scenario_simulation(request.get_json(silent=True) or {}))

    @app.get("/api/agent/delivery-risk")
    def api_agent_delivery_risk():
        return jsonify(delivery_risk_agent())

    @app.get("/api/agent/route-optimization")
    def api_agent_route_optimization():
        return jsonify(route_optimization_agent())

    @app.get("/api/agent/inventory-risk")
    def api_agent_inventory_risk():
        return jsonify(inventory_risk_agent())

    @app.get("/api/agent/carrier-allocation")
    def api_agent_carrier_allocation():
        return jsonify(carrier_allocation_agent())

    @app.get("/api/agent/supplier-risk")
    def api_agent_supplier_risk():
        return jsonify(supplier_risk_agent())

    @app.get("/api/data-management")
    def api_data_management():
        return jsonify(data_management())

    @app.get("/")
    def index():
        return send_from_directory(app.static_folder, "index.html")

    @app.errorhandler(404)
    def spa_fallback(_error):
        if request.path.startswith("/api/"):
            return jsonify({"error": "Not found"}), 404
        return send_from_directory(app.static_folder, "index.html")

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=False)
