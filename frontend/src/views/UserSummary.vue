<template>
    <NavBar />
    <div class="container mx-auto px-4 py-8">
        <h2 class="text-3xl font-bold text-center mb-8 text-gray-800">My Parking Summary</h2>

        <div v-if="loading" class="text-center text-lg text-blue-600">
            Loading your summary data...
        </div>

        <div v-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
            <strong class="font-bold">Error!</strong>
            <span class="block sm:inline"> {{ error }}</span>
        </div>

        <div v-if="!loading && !error" class="grid grid-cols-1 md:grid-cols-2 gap-8">
            <!-- My Total Spending per Parking Lot Chart -->
            <div class="bg-white p-6 rounded-lg shadow-lg">
                <h3 class="text-xl font-semibold mb-4 text-gray-700">My Spending per Parking Lot</h3>
                <canvas id="userSpendingChart"></canvas>
                <p v-if="userSpendingChartData.labels.length === 0" class="text-center text-gray-500 mt-4">
                    No spending data available yet. Make a reservation!
                </p>
            </div>

            <!-- My Reservation Status Chart -->
            <div class="bg-white p-6 rounded-lg shadow-lg">
                <h3 class="text-xl font-semibold mb-4 text-gray-700">My Reservation Status</h3>
                <canvas id="userReservationStatusChart"></canvas>
                <p v-if="userReservationStatusChartData.datasets[0].data[0] === 0 && userReservationStatusChartData.datasets[0].data[1] === 0"
                    class="text-center text-gray-500 mt-4">
                    No reservations found yet.
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
    name: 'UserSummary',
    components: {
        NavBar,
    },
    data() {
        return {
            loading: true,
            error: null,
            lots: [],
            spots: [],
            reservations: [], // These will be only the current user's reservations
            userSpendingChart: null,
            userReservationStatusChart: null,
            userSpendingChartData: {
                labels: [],
                datasets: [{
                    label: 'Total Spending (₹)',
                    backgroundColor: 'rgba(54, 162, 235, 0.6)', // Blue color
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1,
                    data: [],
                }]
            },
            userReservationStatusChartData: {
                labels: ['Active / Future Reservations', 'Completed Reservations'],
                datasets: [{
                    label: 'Number of Reservations',
                    backgroundColor: ['#28A745', '#6C757D'], // Green for active, Gray for completed
                    borderColor: ['#28A745', '#6C757D'],
                    borderWidth: 1,
                    data: [0, 0], // Initial values
                }]
            }
        };
    },
    async mounted() {
        await this.fetchUserSummaryData();
        if (!this.error) {
            this.processDataForCharts();
            this.renderCharts();
        }
    },
    beforeUnmount() {
        // Destroy chart instances to prevent memory leaks
        if (this.userSpendingChart) {
            this.userSpendingChart.destroy();
        }
        if (this.userReservationStatusChart) {
            this.userReservationStatusChart.destroy();
        }
    },
    methods: {
        async fetchUserSummaryData() {
            try {
                const response = await fetch('http://127.0.0.1:5000/user_summary', {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer ' + localStorage.getItem('access_token')
                    }
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    // User-specific error handling, e.g., redirect to login if token invalid
                    toast.error(errorData.message || 'Failed to fetch user summary data.', { position: 'top-center' });
                    // Optionally redirect to login if the user is not authenticated
                    if (response.status === 401 || response.status === 403) {
                        this.$router.push('/login');
                    }
                } else {
                    const data = await response.json();
                    this.lots = data.lots;
                    this.spots = data.spots;
                    this.reservations = data.reservations; // These are already filtered for the user by backend
                }
            } catch (error) {
                this.error = 'Server error or network issue while fetching data.';
                toast.error(this.error, { position: 'top-center' });
                console.error('Error fetching user summary:', error);
            } finally {
                this.loading = false;
            }
        },

        processDataForCharts() {
            // --- Process data for My Total Spending per Parking Lot Chart ---
            const lotSpendingMap = {};
            const lotNamesMap = {};

            // Map lot IDs to names for easy lookup
            this.lots.forEach(lot => {
                lotNamesMap[lot.id] = lot.prime_location_name;
            });

            // Aggregate total_cost for each lot from the user's reservations
            this.reservations.forEach(res => {
                if (res.total_cost !== null && typeof res.total_cost === 'number') {
                    // Find the lot_id for the spot_id in the reservation
                    const spot = this.spots.find(s => s.id === res.spot_id);
                    if (spot) {
                        // Initialize if not present
                        if (!lotSpendingMap.hasOwnProperty(spot.lot_id)) {
                            lotSpendingMap[spot.lot_id] = 0;
                        }
                        lotSpendingMap[spot.lot_id] += res.total_cost;
                    }
                }
            });

            // Populate userSpendingChartData
            this.userSpendingChartData.labels = [];
            this.userSpendingChartData.datasets[0].data = [];
            for (const lotId in lotSpendingMap) {
                if (lotSpendingMap.hasOwnProperty(lotId)) {
                    this.userSpendingChartData.labels.push(lotNamesMap[lotId] || `Lot ${lotId}`);
                    this.userSpendingChartData.datasets[0].data.push(lotSpendingMap[lotId]);
                }
            }

            // --- Process data for My Reservation Status Chart ---
            let activeReservations = 0;
            let completedReservations = 0;
            const currentTime = new Date();

            this.reservations.forEach(res => {
                // Check if exit_time is null (ongoing) or in the future
                if (res.exit_time === null || new Date(res.exit_time) > currentTime) {
                    activeReservations++;
                } else {
                    completedReservations++;
                }
            });

            this.userReservationStatusChartData.datasets[0].data = [activeReservations, completedReservations];
        },

        renderCharts() {
            // Render My Total Spending per Parking Lot Chart (Bar Chart)
            const spendingCtx = document.getElementById('userSpendingChart');
            if (spendingCtx) {
                this.userSpendingChart = new Chart(spendingCtx, {
                    type: 'bar',
                    data: this.userSpendingChartData,
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            y: {
                                beginAtZero: true,
                                title: {
                                    display: true,
                                    text: 'Spending (₹)'
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

            // Render My Reservation Status Chart (Doughnut Chart)
            const statusCtx = document.getElementById('userReservationStatusChart');
            if (statusCtx) {
                this.userReservationStatusChart = new Chart(statusCtx, {
                    type: 'doughnut',
                    data: this.userReservationStatusChartData,
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
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

/* Tailwind CSS classes used for styling (same as AdminSummary for consistency) */
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