/** @odoo-module **/
import { Component, useState, onWillStart, onMounted, useRef } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { loadJS } from "@web/core/assets";

export class SgtDashboard extends Component {
    setup() {
        this.rpc = useService("rpc");
        this.barChartRef = useRef("barChart");
        this.pieChartRef = useRef("pieChart");
        this.state = useState({ isLoading: true, data: {} });

        onWillStart(async () => {
            await loadJS("/web/static/lib/Chart/Chart.js");
            await this.fetchData();
        });
        onMounted(() => { this.renderCharts(); });
    }

    async fetchData() {
        this.state.isLoading = true;
        try {
            const result = await this.rpc("/api/sgt_dashboard/get_kpis", {});
            this.state.data = result;
        } catch (error) { console.error("Lỗi:", error); } 
        finally { this.state.isLoading = false; }
    }

    renderCharts() {
        if (!this.barChartRef.el || !this.pieChartRef.el || !this.state.data.charts) return;
        const chartData = this.state.data.charts;
        new Chart(this.barChartRef.el, {
            type: 'bar',
            data: {
                labels: chartData.stage_labels,
                datasets: [{ label: 'Doanh thu dự kiến', data: chartData.stage_revenues, backgroundColor: '#0d6efd' }]
            },
            options: { responsive: true, maintainAspectRatio: false }
        });
        new Chart(this.pieChartRef.el, {
            type: 'doughnut',
            data: {
                labels: chartData.source_labels,
                datasets: [{ data: chartData.source_counts, backgroundColor: ['#198754', '#ffc107', '#dc3545', '#0dcaf0', '#6f42c1'] }]
            },
            options: { responsive: true, maintainAspectRatio: false }
        });
    }

    formatCurrency(value) {
        if (value >= 1000000000) return (value / 1000000000).toFixed(2) + ' tỷ ₫';
        if (value >= 1000000) return (value / 1000000).toFixed(2) + ' triệu ₫';
        return (value || 0).toLocaleString('vi-VN') + ' ₫';
    }
}
SgtDashboard.template = "sgt_sales_dashboard.Dashboard";
registry.category("actions").add("sgt_sales_dashboard.main", SgtDashboard);
