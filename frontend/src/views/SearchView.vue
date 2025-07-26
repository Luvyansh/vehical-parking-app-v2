<template>
    <NavBar />
    <div class="container d-flex flex-column align-items-center justify-content-center mt-5">
        <h2 class="mb-4 text-center">Admin Search</h2>

        <div class="w-100" style="max-width: 600px;">
            <input v-model="query" @keyup.enter="performSearch" type="text" class="form-control form-control-lg"
                placeholder="Search users, lots, or reservations..." />
        </div>

        <button class="btn btn-primary mt-3" @click="performSearch">Search</button>

        <!-- Users Table -->
        <div class="w-100 mt-5" v-if="results.users.length">
            <h4 class="text-center">Users ({{ results.users.length }})</h4>
            <div class="table-responsive">
                <table class="table table-bordered mt-3">
                    <thead class="table-light">
                        <tr>
                            <th>ID</th>
                            <th>Name</th>
                            <th>Username</th>
                            <th>Email</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="(user, index) in results.users" :key="index">
                            <td>{{ user.ID }}</td>
                            <td>{{ user.Name }}</td>
                            <td>{{ user.Username }}</td>
                            <td>{{ user.Email }}</td>
                            <td>
                                <button class="btn btn-danger" @click="deleteUser(user.ID)">Delete</button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Parking Lots Table -->
        <div class="w-100 mt-5" v-if="results.lots.length">
            <h4 class="text-center">Parking Lots ({{ results.lots.length }})</h4>
            <div class="table-responsive">
                <table class="table table-bordered mt-3">
                    <thead class="table-light">
                        <tr>
                            <th>ID</th>
                            <th>Location</th>
                            <th>Address</th>
                            <th>Pin</th>
                            <th>Price</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="(lot, index) in results.lots" :key="index">
                            <td>{{ lot.ID }}</td>
                            <td>{{ lot.Location }}</td>
                            <td>{{ lot.Address }}</td>
                            <td>{{ lot.Pin }}</td>
                            <td>{{ lot.Price }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Reservations Table -->
        <div class="w-100 mt-5" v-if="results.reservations.length">
            <h4 class="text-center">Reservations ({{ results.reservations.length }})</h4>
            <div class="table-responsive">
                <table class="table table-bordered mt-3">
                    <thead class="table-light">
                        <tr>
                            <th>ID</th>
                            <th>User ID</th>
                            <th>Spot ID</th>
                            <th>Park Time</th>
                            <th>Exit Time</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="(res, index) in results.reservations" :key="index">
                            <td>{{ res.ID }}</td>
                            <td>{{ res["User ID"] }}</td>
                            <td>{{ res["Spot ID"] }}</td>
                            <td>{{ res["Park Time"] }}</td>
                            <td>{{ res["Exit Time"] }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <div v-if="!results.users.length && !results.lots.length && !results.reservations.length && searched"
            class="text-muted mt-4">
            No matching results found.
        </div>
    </div>
</template>

<script>
import NavBar from '@/components/NavBar.vue';
import { toast } from 'vue3-toastify';

export default {
    name: 'SearchView',
    components: { NavBar },
    data() {
        return {
            query: '',
            results: {
                users: [],
                lots: [],
                reservations: []
            },
            searched: false
        };
    },
    computed: {
        totalResults() {
            return (
                this.results.users.length +
                this.results.lots.length +
                this.results.reservations.length
            );
        }
    },
    async mounted() {
        try {
            const res = await fetch('http://127.0.0.1:5000/admin_dashboard');
            if (!res.ok) {
                toast.error('Unauthorized or server error.', {
                    position: 'top-center',
                    onClose: () => {
                        this.$router.push('/admin_dashboard');
                    },
                });
            }
            const data = await res.json();
            this.results.users = data.users;
            this.results.lots = data.lots;
            this.results.reservations = data.reservations;
        } catch (err) {
            console.error(err);
            toast.error('Failed to fetch search results.', { position: 'top-center' });
        }
    },
    methods: {
        async deleteUser(id) {
            try {
                const res = await fetch(`http://127.0.0.1:5000/delete_user/${id}`, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer ' + localStorage.getItem('access_token')
                    }
                });

                if (!res.ok) {
                    toast.error('Unauthorized or server error.', { position: 'top-center' });
                    return;
                }

                toast.success('User deleted successfully.', { position: 'top-center' });

                // Remove user from the results after successful delete
                this.results.users = this.results.users.filter(user => user.ID !== id);

            } catch (err) {
                console.error(err);
                toast.error('Delete failed.', { position: 'top-center' });
            }
        },

        async performSearch() {
            this.searched = true;
            this.results = { users: [], lots: [], reservations: [] };

            if (!this.query.trim()) {
                toast.warning('Enter a search query.', { position: 'top-center' });
                return;
            }

            try {
                const res = await fetch(`http://127.0.0.1:5000/search?q=${encodeURIComponent(this.query)}`, {
                    method: 'GET',
                    headers: {
                        'Authorization': 'Bearer ' + localStorage.getItem('access_token')
                    }
                });

                if (!res.ok) {
                    toast.error('Unauthorized or server error.', { position: 'top-center' });
                    return;
                }

                const data = await res.json();
                this.results = data;
            } catch (err) {
                console.error(err);
                toast.error('Search failed.', { position: 'top-center' });
            }
        }
    }
};
</script>