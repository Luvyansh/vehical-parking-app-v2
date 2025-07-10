<template>
    <div class="container mt-5 text-center">
        <h2>Admin Dashboard</h2>
        <p>{{ adminMessage }}</p>
    </div>
</template>

<script>
    import { toast } from 'vue3-toastify';

    export default {
        name: 'AdminView',
        data() {
            return {
            adminMessage: ''
            };
        },
        async mounted() {
            try {
            const response = await fetch('http://localhost:5000/admin_dashboard', {
                method: 'GET',
                mode: 'cors',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include', // 🧠 session-based auth
            });

            const data = await response.json();

            if (!response.ok) {
                toast.error(data.message || 'Access denied');
                this.$router.push('/login');
            } else {
                this.adminMessage = data.message;
                toast.success(data.message);
            }
            } catch (error) {
            toast.error('Server error while loading admin dashboard.');
            console.error(error);
            }
        }
    };
</script>

<style scoped>
    .container {
        max-width: 600px;
        margin: 0 auto;
    }
</style>