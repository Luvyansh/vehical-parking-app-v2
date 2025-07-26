<template>
    <NavBar />
    <div class="container py-5">

        <!-- Header -->
        <div class="text-center mb-5">
            <h2 class="fw-bold">User Dashboard</h2>
        </div>

        <!-- User Reservations Section -->
        <div v-if="userReservations.length > 0" class="mb-5">
            <div class="card shadow border-0">
                <div class="card-header bg-primary text-white text-center">
                    <h4 class="mb-0">Your Reservations</h4>
                </div>
                <div class="card-body p-4">
                    <div class="table-responsive">
                        <table class="table table-striped align-middle mb-0">
                            <thead class="table-light">
                                <tr>
                                    <th scope="col" class="text-center">ID</th>
                                    <th scope="col" class="text-center">Spot ID</th>
                                    <th scope="col" class="text-center">Park Time</th>
                                    <th scope="col" class="text-center">Exit Time</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="reservation in userReservations" :key="reservation.id">
                                    <td class="text-center">{{ reservation.id }}</td>
                                    <td class="text-center">{{ reservation.spot_id }}</td>
                                    <td class="text-center">{{ formatDateTime(reservation.park_time) }}</td>
                                    <td class="text-center">{{ formatDateTime(reservation.exit_time) }}</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>

        <!-- Divider -->
        <hr class="my-5" />

        <!-- Search Section -->
        <div class="text-center">
            <h4 class="mb-4 text-secondary">Search Parking Lots by Location, Pincode or Price</h4>
            <div class="d-flex justify-content-center">
                <div class="input-group" style="max-width: 400px;">
                    <input v-model="query" type="text" class="form-control" placeholder="Enter query..." />
                    <button class="btn btn-primary" @click="performSearch">Search</button>
                </div>
            </div>
        </div>

    </div>
</template>

<script>
import NavBar from '@/components/NavBar.vue';
import { toast } from 'vue3-toastify';

export default {
    name: 'UserView',
    components: {
        NavBar,
    },
    data() {
        return {
            username: '',
            userReservations: [],
        };
    },
    async mounted() {
        const token = localStorage.getItem('access_token');
        if (!token) {
            toast.error('No access token found.', { position: 'top-center' });
            this.$router.push('/login');
            return;
        }

        try {
            const response = await fetch('http://127.0.0.1:5000/user_dashboard', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
            });

            if (!response.ok) {
                toast.error('Access Denied.', {
                    position: 'top-center',
                    onClose: () => this.$router.push('/login'),
                });
                return;
            }

            await this.getUserInfo();
            if (this.username) {
                await this.getUserReservations();
            } else {
                toast.error('Username not found.', { position: 'top-center' });
            }
        } catch (error) {
            toast.error('Server error.', { position: 'top-center' });
            console.error(error);
        }
    },
    methods: {
        async getUserReservations() {
            try {
                const res = await fetch(`http://127.0.0.1:5000/get_user_reservations/${this.username}`, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                    },
                    credentials: 'include',
                });

                if (!res.ok) {
                    toast.error('Failed to fetch reservations.', { position: 'top-center' });
                    return;
                }

                const data = await res.json();
                this.userReservations = data.reservations;
            } catch (error) {
                console.error(error);
            }
        },
        async getUserInfo() {
            try {
                const res = await fetch('http://127.0.0.1:5000/get_user_info', {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer ' + localStorage.getItem('access_token'),
                    },
                });

                if (!res.ok) {
                    toast.error('Failed to fetch user info.', { position: 'top-center' });
                    return;
                }

                const data = await res.json();
                this.username = data.user.username;  // ✅ correct access
            } catch (error) {
                console.error(error);
            }
        },
        async performSearch() {
            try {
                const res = await fetch(`http://127.0.0.1:5000/user_search?q=${encodeURIComponent(this.query)}`, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer ' + localStorage.getItem('access_token'),
                    }
                });
                if (!res.ok) {
                    toast.error('Failed to perform search.', { position: 'top-center' });
                    return;
                }
                const data = await res.json();
                this.results = data.results;
            } catch (error) {
                console.error(error);
            }
        },
        formatDateTime(datetimeStr) {
            const options = {
                year: 'numeric',
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
            };
            return new Date(datetimeStr).toLocaleString(undefined, options);
        },
    },
};
</script>

<style scoped>
.card-header {
    font-size: 1.25rem;
    font-weight: 600;
}
</style>