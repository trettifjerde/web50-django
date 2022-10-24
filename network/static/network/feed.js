let handlePostScroll;
const app = Vue.createApp({
    template: `<new-post-form v-if="isNewPostFormVisible()" @post="addNewPost"/> 
    <div ref="mainErrorMsg" v-show="errorMsg" class="error-msg">{{ errorMsg }}</div>
    <post v-for="post in feedPosts" :post="post" :key="post.id" @update="updatePost" @error="showError"/>
    <div v-show="loadStatusMsg" class="c">{{ loadStatusMsg }}</div>`,
    data() {
        return {
            currentPage: 0,
            pending: false,
            errorMsg: '',
            loadStatusMsg: '',
            postsPerPage: 10,
            signedIn: signedIn,
            feedType: feedType,
            feedPosts: [],
            message: '',
            messageType: '',
        }
    },
    watch: {
        errorMsg(current, _) {
            if (current) this.$nextTick(() => this.$refs.mainErrorMsg.scrollIntoView({behavior: 'smooth', block: 'end'}));
        }
    },
    methods: {
        async getMorePosts() {
            this.currentPage++;
            this.pending = true;
            this.loadStatusMsg = 'Loading...';

            const url = `/network/morePosts/?page=${this.currentPage}&feedType=${this.feedType}`;

            return await fetch(url, {
                headers: {'X-Requested-With': 'XMLHttpRequest'}
            })
            .then(res => res.json())
            .then(data => {
                this.pending = false;

                if ('posts' in data) {
                    data.posts.forEach(post => this.feedPosts.push(post));

                    if (data.posts.length === 0) {
                        this.loadStatusMsg = 'No posts yet.';
                        document.removeEventListener('scroll', handlePostScroll);
                    }
                    else if (data.posts.length % 10 !== 0) {
                        this.loadStatusMsg = 'No more posts to load.';
                        document.removeEventListener('scroll', handlePostScroll);
                    }
                    else
                        this.loadStatusMsg = '';
                }
                else 
                    this.errorMsg = 'Problem loading posts. Try again later.';
            })
            .catch(err => console.log(err))
        },
        updatePost(eventType, info) {
            const i = this.feedPosts.findIndex(p => p.id === info.id);
            switch(eventType) {
                case 'remove':
                    this.feedPosts.splice(i, 1);
                    break;
                case 'edit':
                case 'like':
                    const post = this.feedPosts[i];
                    Object.entries(info).forEach(([key, value]) => post[key] = value);
                    break;
            }
        },
        addNewPost(post) {
            this.feedPosts.splice(0, 0, post);
        },
        isNewPostFormVisible() {
            switch(this.feedType) {
                case 'self':
                    return true;
                case 'all':
                    if (this.signedIn) return true;
                default:
                    return false;
            }
        },
        handlePostScroll() {
            if(document.documentElement.scrollTop > document.documentElement.offsetHeight - 2 * window.innerHeight) {
                if (! this.pending) this.getMorePosts();
            }
        },
        showError(msg) {
            this.errorMsg = msg;
        }
    },
    async created() {
        handlePostScroll = this.handlePostScroll.bind(this);
        document.addEventListener('scroll', handlePostScroll);
        this.getMorePosts();
    },

});

app.component('post', {
    template: `<div class="post">
    <div v-show="!editFormVisible && !deleteConfirmationVisible" class="post-post">
        <div class="post-header">
            <div class="post-avatar">
                <img :src="post.avatar">
            </div>
            <div>
                <p class="b"><a :href="getNetworkerUrl()">{{ post.networker }}</a></p>
                <div class="extra">
                    <span>
                        <span class="b">Created: </span>{{ post.created }}
                    </span>
                    <span v-if="post.created !== post.edited">
                        <span class="b">Edited: </span>
                        <span class="last-edited">{{ post.edited }}</span> 
                    </span>
                </div>
            </div>
            <div class="spacer"></div>     
            <button v-if="post.self" class="btn-sm" @click="togglePostEditForm()">Edit</button>
            <button v-if="post.self" class="btn-sm" @click="toggleDeletePost()">Delete</button>
        </div>
        <div class="post-body" v-html="post.text"></div>
        <div class="post-footer">
            <button v-if="getSignedStatus()" class="btn btn-likes" @click="like()">
                <div :class="getLikeClass()"></div>
                <span class="num-likes">{{ post.likes }}</span>
            </button>
            <button v-else class="btn btn-likes" disabled title="Sign in to leave likes">
                <div class="heart"></div>
                <span class="num-likes">{{ post.likes }}</span>
            </button>
        </div>
    </div>
    <div v-if="post.self" v-show="editFormVisible || deleteConfirmationVisible" class="post-meta">
        <form v-show="editFormVisible">
            <p v-show="editFormErrorMessage" class="error-msg">{{ editFormErrorMessage }}</p>
            <textarea name="text" v-model="editedPostText" required></textarea>
            <button type="submit" @click.prevent="savePost()">Save</button>
            <button type="button" @click="togglePostEditForm()">Cancel</button>
        </form>
        <div v-show="deleteConfirmationVisible" class="post-meta">
            <div class="post-meta-msg">Are you sure you want to delete this post?</div>
            <button type="button" @click="deletePost()">Confirm</button>
            <button type="button" @click="toggleDeletePost()">Cancel</button>
        </div>
    </div>
</div>`,
    data() {
        return {
            editedPostText: '',
            editFormVisible: false,
            editFormErrorMessage: '',
            deleteConfirmationVisible: false,
        }
    },
    props: ['post'],
    methods: {
        getLikeClass() {
            return `heart ${this.post.liked ? 'liked' : ''}`; 
        },
        getSignedStatus() {
            return signedIn;
        },
        getNetworkerUrl() {
            return `/network/user/${this.post.networkerId}/`;
        },
        togglePostEditForm() {
            this.editedPostText = this.post.text;
            this.editFormVisible = ! this.editFormVisible;
            this.editFormErrorMessage = '';
        },
        toggleDeletePost() {
            this.deleteConfirmationVisible = !this.deleteConfirmationVisible;
        },
        savePost() {
            if (this.editedPostText === this.post.text)
            {
                this.editFormErrorMessage = "You haven't changed anything";
            }
            else 
            {
                fetch('/network/editPost/', {
                    method: 'POST',
                    headers: getAjaxHeaders(),
                    body: JSON.stringify({postId: this.post.id, text: this.editedPostText})
                })
                .then(res => res.json())
                .then(data => {
                    if ('post' in data) this.updatePost(data.post);
                    else if ('error' in data) this.editFormErrorMessage = data.error;
                    else throw data;
                })
                .catch(err => {
                    this.editFormErrorMessage = 'An error has occured';
                    console.log(err)
                });
            }
        },
        updatePost(post) {
            this.$emit('update', 'edit', post);
            this.togglePostEditForm();
        },
        deletePost() {
            fetch('/network/deletePost/', {
                method: 'POST',
                headers: getAjaxHeaders(),
                body: JSON.stringify({postId: this.post.id})
            })
            .then(res => res.json())
            .then(data => {      
                if ('error' in data) this.$emit('error', data.error);
                else if ('ok' in data) this.$emit('update', 'remove', {id:this.post.id});
                else throw data;
            })
            .catch(err => console.log(err));
        },
        like() {
            fetch('/network/like/', {
                method: 'PUT',
                headers: getAjaxHeaders(),
                body: JSON.stringify({post_id: this.post.id})
            })
            .then(res => res.json())
            .then(data => {
                if ('error' in data) this.$emit('error', data.error);
                else if ('likes' in data) {
                    this.$emit('update', 'like', {
                        id: this.post.id, 
                        likes: data.likes, 
                        liked: !this.post.liked,
                    });
                }
                else throw data;
            })
            .catch(err => console.log(err));
        }
    }
});

app.component('new-post-form', {
    template: `<div>
    <h2>New post</h2>
    <form @submit.prevent="post()">
        <p v-show="errorMsg" class="error-msg">{{ errorMsg }}</p>
        <textarea v-model="text" @focus="hideError()" name="text" placeholder="What's up?"></textarea>
        <button type="submit">Post</button> 
    </form>
</div>`,
    data() { 
        return {
            text: '',
            errorMsg: ''
        }
    },
    methods: {
        post() {
            if (this.text) {
                fetch('/network/new/', {
                    method: 'POST',
                    headers: getAjaxHeaders(),
                    body: JSON.stringify({text: this.text})
                })
                .then(res => res.json())
                .then(data => {
                    if ('error' in data) this.errorMsg = data.error;
                    else if ('post' in data) {
                        this.$emit('post', data.post);
                        this.text = '';
                    }
                    else throw data;
                }, _ => this.errorMsg = 'Reload the page and try again')
                .catch(err => console.log(err));
            }
            else this.errorMsg = 'Cannot be empty';
        },
        hideError() { this.errorMsg = ''; }
    },
});

app.mount('#feed');