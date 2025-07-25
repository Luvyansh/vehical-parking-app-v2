<template>
    <NavBar />
    <div class="container mt-5">
        <h2 class="text-center mb-4">User Manager</h2>
        <table class="table table-bordered table-hover">
            <thead class="table-light">
                <tr>
                    <th>Name</th>
                    <th>Username</th>
                    <th>Email</th>
                    <th>Reserved Spots</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="user in users" :key="user.id">
                    <td>{{ user.name }}</td>
                    <td>{{ user.username }}</td>
                    <td>{{ user.email }}</td>
                    <td>{{ user.reserved_spots }}</td>
                    <td>
                        <button class="btn btn-danger" @click="deleteUser(user.id)">Delete</button>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
</template>

<script>
import NavBar from '@/components/NavBar.vue';
import { toast } from 'vue3-toastify';

export default {
    name: 'UserManagerView',
    components: {
        NavBar,
    },
    data() {
        return {
            users: [],
            reservations: []
        };
    },
    async mounted() {
        try {
            const response = await fetch('http://127.0.0.1:5000/admin_dashboard', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + localStorage.getItem('access_token')
                }
            });

            if (!response.ok) {
                toast.error('Access Denied: You are logged in as a user.', { position: 'top-center' });
                this.$router.push('/user_dashboard');
            } else {
                await this.getLots();   // Get reservations first
                await this.getUsers();  // Then attach reservation counts
            }
        } catch (error) {
            toast.error('Server error.', { position: 'top-center' });
            console.error(error);
        }
    },
    methods: {
        async getLots() {
            try {
                const response = await fetch('http://127.0.0.1:5000/parking_lots', {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                    }
                });
                const data = await response.json();
                this.reservations = data.reservedSpots;
            } catch (error) {
                console.error(error);
                toast.error('Failed to fetch reservation data.', { position: 'top-center' });
            }
        },
        async getUsers() {
            try {
                const response = await fetch('http://127.0.0.1:5000/get_users', {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                    }
                });
                const data = await response.json();

                // Count reservations per user
                const reservationCounts = {};
                for (const reservation of this.reservations) {
                    const userId = reservation.user_id;
                    reservationCounts[userId] = (reservationCounts[userId] || 0) + 1;
                }

                // Attach reserved_spots count to each user
                this.users = data.users.map(user => ({
                    ...user,
                    reserved_spots: reservationCounts[user.id] || 0
                }));
            } catch (error) {
                console.error(error);
                toast.error('Failed to fetch user data.', { position: 'top-center' });
            }
        },
        async deleteUser(userId) {
            try {
                const response = await fetch(`http://127.0.0.1:5000/delete_user/${userId}`, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                    }
                });
                if (response.ok) {
                    toast.success('User deleted successfully.', { position: 'top-center' });
                    this.getUsers();
                } else {
                    toast.error('Failed to delete user.', { position: 'top-center' });
                }
            } catch (error) {
                console.error(error);
                toast.error('Failed to delete user.', { position: 'top-center' });
            }
        }
    }
};
</script>