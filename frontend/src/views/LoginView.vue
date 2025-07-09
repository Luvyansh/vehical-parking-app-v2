    <template>
        <div class="container mt-5">
            <h2 class="text-center mb-4">Login</h2>
            <div class="home-form bg-light p-4 rounded shadow">
            <form @submit.prevent="login">
                <div class="form-group mb-3">
                <label for="username">Username</label>
                <input type="text" v-model="username" class="form-control" id="username" placeholder="Enter Username" required>
                </div>
                <div class="form-group mb-3">
                <label for="password">Password</label>
                <input type="password" v-model="password" class="form-control" id="password" placeholder="Enter password" required>
                </div>
                <button type="submit" class="btn btn-primary">Login</button>
            </form>
            </div>
        </div>
    </template>

    <script>
        import { toast } from 'vue3-toastify';

        export default {
        data() {
            return {
            username: '',
            password: '',
            };
        },
        methods: {
            async login() {
            try {
                const response = await fetch('http://127.0.0.1:5000/login', {
                method: 'POST',
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
                } else {
                // 🧹 Clear previous data
                localStorage.removeItem('token');
                localStorage.removeItem('username');
                localStorage.removeItem('isAdmin');

                // ✅ Save new data
                localStorage.setItem('token', data.token);
                localStorage.setItem('username', this.username);
                localStorage.setItem('isAdmin', data.admin);

                toast.success(data.message || 'Login successful', {
                    position: 'top-center',
                    onClose: () => {
                    const targetRoute = data.admin ? '/admin_dashboard' : '/user_dashboard';
                    this.$router.push(targetRoute);
                    }
                });
                }
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