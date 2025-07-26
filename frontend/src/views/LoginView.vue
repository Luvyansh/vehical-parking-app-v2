<template>
    <NavBar />
    <div class="container mt-5">
        <h2 class="text-center mb-4">Login</h2>
        <div class="home-form bg-neutral p-4 rounded shadow">
            <form @submit.prevent="login">
                <div class="form-group mb-3">
                    <label for="username">Username</label>
                    <input type="text" v-model="username" class="bg-light form-control" id="username"
                        placeholder="Enter Username" required>
                </div>
                <div class="form-group mb-3">
                    <label for="password">Password</label>
                    <input type="password" v-model="password" class="bg-light form-control" id="password"
                        placeholder="Enter password" required>
                </div>
                <button type="submit" class="btn btn-primary">Login</button>
            </form>
        </div>
    </div>
</template>

<script>
import NavBar from '@/components/NavBar.vue';
import { toast } from 'vue3-toastify';

export default {
    data() {
        return {
            username: '',
            password: '',
        };
    },
    components: {
        NavBar,
    },
    methods: {
        async login() {
            try {
                const response = await fetch('http://127.0.0.1:5000/login', {
                    method: 'POST',
                    credentials: 'include',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        username: this.username,
                        password: this.password,
                    }),
                });
                const data = await response.json();
                if (!response.ok) {
                    toast.error(data.message || 'Login failed', { position: 'top-center' });
                    return;
                }
                // ✅ Store token
                localStorage.setItem('access_token', data.access_token);
                toast.success(data.message || 'Login successful', {
                    position: 'top-center',
                    onClose: async () => {
                        // ✅ Fetch user info with token
                        const token = localStorage.getItem('access_token');
                        const userInfoResponse = await fetch('http://127.0.0.1:5000/get_user_info', {
                            method: 'GET',
                            headers: {
                                'Content-Type': 'application/json',
                                'Authorization': `Bearer ${token}`,
                            },
                            credentials: 'include',
                        });
                        const userInfo = await userInfoResponse.json();
                        if (userInfo.user && userInfo.user.admin === true) {
                            this.$router.push('/admin_dashboard');
                        } else {
                            this.$router.push('/user_dashboard');
                        }
                    }
                });
            } catch (error) {
                toast.error('Server error. Try again later.', { position: 'top-center' });
                console.error(error);
            }
        }
    }
};
</script>

<style scoped>
.home-form {
    max-width: 400px;
    margin: 0 auto;
}
</style>