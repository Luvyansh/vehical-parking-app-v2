import { toast } from 'vue3-toastify';

export default {
    data(){
        return{
            user: null,
            loggedIn: false,
            admin: false
        }
    },
    async created(){
        await this.userStatus();
    },
    methods: {
        async userStatus(){
            const access_token = localStorage.getItem('access_token');
            if (!access_token) {
                this.user = null;
                this.loggedIn = false;
                this.admin = false;
                return;
            }
            this.user = await this.getUserInfo(access_token);
            if (this.user) {
                this.loggedIn = true;
                this.admin = this.user.admin;
            }
        },
        async getUserInfo(access_token){
            const response = await fetch('http://127.0.0.1:5000/get_user_info', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${access_token}`
                },
            });
            if (!response.ok) {
                this.loggedIn = false;
                this.admin = false;
                console.log("response not ok");
                return null;
            }
            const data = await response.json();
            return data.user;
        },
        async logout() {
            const response = await fetch('http://127.0.0.1:5000/logout', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                },
            })
            if(response.ok) {
                toast.success(response.json().message || 'Logout successful', {
                    position: 'top-center',
                    onClose: () => {
                        localStorage.removeItem('access_token');
                        this.$router.push("/login");
                    }
                });
            }
        }
    }
}