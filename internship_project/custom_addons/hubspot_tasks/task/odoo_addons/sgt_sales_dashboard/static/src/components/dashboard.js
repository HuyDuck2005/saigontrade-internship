/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Component, onWillStart, onMounted, useState, useRef } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { loadJS } from "@web/core/assets";

export class SalesDashboard extends Component {
    setup() {
        this.orm = useService("orm");
        this.barChartRef = useRef("barChart");
        this.pieChartRef = useRef("pieChart");

        this.state = useState({
            kpi: { total_deals: 0, total_revenue: "0 đ", won_deals: 0, win_rate: "0%" },
            charts: { pipeline_labels: [], pipeline_revenues: [], source_labels: [], source_counts: [] },
            filter: 'this_month',
            barType: 'bar', // Mặc định biểu đồ cột, cho phép đổi sang line
            pieType: 'doughnut' // Mặc định biểu đồ tròn
        });

        this.chartInstances = {};

        onWillStart(async () => {
            await loadJS("/web/static/lib/Chart/Chart.js");
            await this.loadData();
        });

        onMounted(() => {
            this.renderCharts();
        });
    }

    async loadData() {
        const data = await this.orm.call("crm.lead", "get_dashboard_stats", [this.state.filter]);
        Object.assign(this.state.kpi, data.kpi);
        Object.assign(this.state.charts, data.charts);
    }

    async onChangeFilter(ev) {
        this.state.filter = ev.target.value;
        await this.loadData();
        this.renderCharts();
    }

    changeBarType(type) {
        this.state.barType = type;
        this.renderCharts();
    }

    changePieType(type) {
        this.state.pieType = type;
        this.renderCharts();
    }

    renderCharts() {
        if (this.chartInstances.bar) this.chartInstances.bar.destroy();
        if (this.chartInstances.pie) this.chartInstances.pie.destroy();

        const barCtx = this.barChartRef.el.getContext('2d');
        this.chartInstances.bar = new Chart(barCtx, {
            type: this.state.barType,
            data: {
                labels: this.state.charts.pipeline_labels,
                datasets: [{
                    label: 'Doanh Thu Dự Kiến (VNĐ)',
                    data: this.state.charts.pipeline_revenues,
                    backgroundColor: '#3b82f6',
                    borderColor: '#1d4ed8',
                    borderWidth: 1,
                    borderRadius: 4
                }]
            },
            options: { responsive: true, maintainAspectRatio: false }
        });

        const pieCtx = this.pieChartRef.el.getContext('2d');
        this.chartInstances.pie = new Chart(pieCtx, {
            type: this.state.pieType,
            data: {
                labels: this.state.charts.source_labels,
                datasets: [{
                    data: this.state.charts.source_counts,
                    backgroundColor: ['#f59e0b', '#10b981', '#3b82f6', '#ef4444', '#8b5cf6']
                }]
            },
            options: { responsive: true, maintainAspectRatio: false }
        });
    }
}
SalesDashboard.template = "sgt_sales_dashboard.Dashboard";
registry.category("actions").add("sgt_sales_dashboard.main", SalesDashboard);
