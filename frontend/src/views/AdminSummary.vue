<template>
    <NavBar />
    <div class="container mx-auto px-4 py-8">
        <h2 class="text-3xl font-bold text-center mb-8 text-gray-800">Admin Summary Dashboard</h2>

        <div v-if="loading" class="text-center text-lg text-blue-600">
            Loading summary data...
        </div>

        <div v-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
            <strong class="font-bold">Error!</strong>
            <span class="block sm:inline"> {{ error }}</span>
        </div>

        <div v-if="!loading && !error" class="grid grid-cols-1 md:grid-cols-2 gap-8">
            <!-- Lot-wise Revenue Chart -->
            <div class="bg-white p-6 rounded-lg shadow-lg">
                <h3 class="text-xl font-semibold mb-4 text-gray-700">Lot-wise Revenue Generated</h3>
                <canvas id="revenueChart"></canvas>
                <p v-if="revenueChartData.labels.length === 0" class="text-center text-gray-500 mt-4">
                    No revenue data available yet.
                </p>
            </div>

            <!-- Spots Availability Chart -->
            <div class="bg-white p-6 rounded-lg shadow-lg">
                <h3 class="text-xl font-semibold mb-4 text-gray-700">Spots Availability</h3>
                <canvas id="spotsChart"></canvas>
                <p v-if="spotsChartData.labels.length === 0" class="text-center text-gray-500 mt-4">
                    No spot data available yet.
                </p>
            </div>
        </div>
    </div>
</template>

<script>
import NavBar from '@/components/NavBar.vue';
import { toast } from 'vue3-toastify';
import { Chart, registerables } from 'chart.js';

// Register all Chart.js components (chart types, scales, plugins etc.)
Chart.register(...registerables);

export default {
    name: 'AdminSummary',
    components: {
        NavBar,
    },
    data() {
        return {
            loading: true,
            error: null,
            lots: [],
            spots: [],
            reservations: [],
            users: [],
            revenueChart: null, // To store the Chart.js instance for revenue
            spotsChart: null,   // To store the Chart.js instance for spots
            revenueChartData: {
                labels: [],
                datasets: [{
                    label: 'Total Revenue (₹)',
                    backgroundColor: 'rgba(75, 192, 192, 0.6)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1,
                    data: [],
                }]
            },
            spotsChartData: {
                labels: ['Available Spots', 'Booked Spots'],
                datasets: [{
                    label: 'Number of Spots',
                    backgroundColor: ['#4CAF50', '#FFC107'], // Green for available, Amber for booked
                    borderColor: ['#4CAF50', '#FFC107'],
                    borderWidth: 1,
                    data: [0, 0], // Initial values
                }]
            }
        };
    },
    async mounted() {
        await this.fetchAdminSummaryData();
        if (!this.error) {
            this.processDataForCharts();
            this.renderCharts();
        }
    },
    beforeUnmount() {
        // Destroy chart instances to prevent memory leaks
        if (this.revenueChart) {
            this.revenueChart.destroy();
        }
        if (this.spotsChart) {
            this.spotsChart.destroy();
        }
    },
    methods: {
        async fetchAdminSummaryData() {
            try {
                const response = await fetch('http://127.0.0.1:5000/admin_summary', {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer ' + localStorage.getItem('access_token')
                    }
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    if (response.status === 401 || response.status === 403) {
                        toast.error('Access Denied: You are not authorized to view this page.', { position: 'top-center' });
                        this.$router.push('/user_dashboard'); // Redirect if not authorized
                    } else {
                        this.error = errorData.message || 'Failed to fetch admin summary data.';
                        toast.error(this.error, { position: 'top-center' });
                    }
                } else {
                    const data = await response.json();
                    this.lots = data.lots;
                    this.spots = data.spots;
                    this.reservations = data.reservations;
                    this.users = data.users; // Though not used for charts, good to have the data
                }
            } catch (error) {
                this.error = 'Server error or network issue while fetching data.';
                toast.error(this.error, { position: 'top-center' });
                console.error('Error fetching admin summary:', error);
            } finally {
                this.loading = false;
            }
        },

        processDataForCharts() {
            // --- Process data for Lot-wise Revenue Chart ---
            const lotRevenueMap = {};
            const lotNamesMap = {};

            // Initialize revenue for each lot to 0 and map lot IDs to names
            this.lots.forEach(lot => {
                lotRevenueMap[lot.id] = 0;
                lotNamesMap[lot.id] = lot.prime_location_name;
            });

            // Aggregate total_cost for each lot from reservations
            this.reservations.forEach(res => {
                // Ensure total_cost is a number and not null/undefined
                if (res.total_cost !== null && typeof res.total_cost === 'number') {
                    // Find the lot_id for the spot_id in the reservation
                    const spot = this.spots.find(s => s.id === res.spot_id);
                    if (spot && lotRevenueMap.hasOwnProperty(spot.lot_id)) {
                        lotRevenueMap[spot.lot_id] += res.total_cost;
                    }
                }
            });

            // Populate revenueChartData
            this.revenueChartData.labels = [];
            this.revenueChartData.datasets[0].data = [];
            for (const lotId in lotRevenueMap) {
                if (lotRevenueMap.hasOwnProperty(lotId)) {
                    this.revenueChartData.labels.push(lotNamesMap[lotId] || `Lot ${lotId}`);
                    this.revenueChartData.datasets[0].data.push(lotRevenueMap[lotId]);
                }
            }

            // --- Process data for Spots Availability Chart ---
            let availableCount = 0;
            let bookedCount = 0;

            this.spots.forEach(spot => {
                if (spot.is_available) {
                    availableCount++;
                } else {
                    bookedCount++;
                }
            });

            this.spotsChartData.datasets[0].data = [availableCount, bookedCount];
        },

        renderCharts() {
            // Render Lot-wise Revenue Chart (Bar Chart)
            const revenueCtx = document.getElementById('revenueChart');
            if (revenueCtx) {
                this.revenueChart = new Chart(revenueCtx, {
                    type: 'bar',
                    data: this.revenueChartData,
                    options: {
                        responsive: true,
                        maintainAspectRatio: false, // Allow canvas to resize freely
                        scales: {
                            y: {
                                beginAtZero: true,
                                title: {
                                    display: true,
                                    text: 'Revenue (₹)'
                                }
                            },
                            x: {
                                title: {
                                    display: true,
                                    text: 'Parking Lot'
                                }
                            }
                        },
                        plugins: {
                            legend: {
                                display: false,
                            },
                            tooltip: {
                                callbacks: {
                                    label: function (context) {
                                        let label = context.dataset.label || '';
                                        if (label) {
                                            label += ': ';
                                        }
                                        if (context.parsed.y !== null) {
                                            label += new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' }).format(context.parsed.y);
                                        }
                                        return label;
                                    }
                                }
                            }
                        }
                    }
                });
            }

            // Render Spots Availability Chart (Doughnut Chart)
            const spotsCtx = document.getElementById('spotsChart');
            if (spotsCtx) {
                this.spotsChart = new Chart(spotsCtx, {
                    type: 'doughnut',
                    data: this.spotsChartData,
                    options: {
                        responsive: true,
                        maintainAspectRatio: false, // Allow canvas to resize freely
                        plugins: {
                            legend: {
                                position: 'top',
                            },
                            tooltip: {
                                callbacks: {
                                    label: function (context) {
                                        let label = context.label || '';
                                        if (label) {
                                            label += ': ';
                                        }
                                        if (context.parsed !== null) {
                                            label += context.parsed;
                                        }
                                        return label;
                                    }
                                }
                            }
                        }
                    }
                });
            }
        }
    }
};
</script>

<style scoped>
/* Ensure the container and charts are responsive */
.container {
    max-width: 1200px;
}

canvas {
    max-height: 400px;
    /* Limit chart height for better display */
    width: 100% !important;
    /* Override Chart.js inline styles if needed */
    height: auto !important;
    /* Override Chart.js inline styles if needed */
}

/* Tailwind CSS classes used for styling */
.mx-auto {
    margin-left: auto;
    margin-right: auto;
}

.px-4 {
    padding-left: 1rem;
    padding-right: 1rem;
}

.py-8 {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

.text-3xl {
    font-size: 1.875rem;
}

.font-bold {
    font-weight: 700;
}

.text-center {
    text-align: center;
}

.mb-8 {
    margin-bottom: 2rem;
}

.text-gray-800 {
    color: #1f2937;
}

.text-lg {
    font-size: 1.125rem;
}

.text-blue-600 {
    color: #2563eb;
}

.bg-red-100 {
    background-color: #fee2e2;
}

.border {
    border-width: 1px;
}

.border-red-400 {
    border-color: #f87171;
}

.text-red-700 {
    color: #b91c1c;
}

.px-4 {
    padding-left: 1rem;
    padding-right: 1rem;
}

.py-3 {
    padding-top: 0.75rem;
    padding-bottom: 0.75rem;
}

.rounded {
    border-radius: 0.25rem;
}

.relative {
    position: relative;
}

.font-bold {
    font-weight: 700;
}

.block {
    display: block;
}

.sm:inline {
    /* For small screens and up, display inline */
}

.grid {
    display: grid;
}

.grid-cols-1 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
}

.md:grid-cols-2 {
    /* For medium screens and up, 2 columns */
}

.gap-8 {
    gap: 2rem;
}

.bg-white {
    background-color: #fff;
}

.p-6 {
    padding: 1.5rem;
}

.rounded-lg {
    border-radius: 0.5rem;
}

.shadow-lg {
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

.text-xl {
    font-size: 1.25rem;
}

.font-semibold {
    font-weight: 600;
}

.mb-4 {
    margin-bottom: 1rem;
}

.text-gray-700 {
    color: #374151;
}

.mt-4 {
    margin-top: 1rem;
}

.text-gray-500 {
    color: #6b7280;
}
</style>