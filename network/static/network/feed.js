const app = Vue.createApp({
    template: `<new-post-form v-if="isNewPostFormVisible()" @post="addNewPost"/> 
    <div ref="mainErrorMsg" v-show="errorMsg" class="error-msg">{{ errorMsg }}</div>
    <transition-group tag="div" class="feed" name="feed">
        <post v-for="post in feedPosts" :post="post" :key="post.id" @update="handleUpdate"/>
    </transition-group>
    <div v-show="loadStatusMsg" class="c">{{ loadStatusMsg }}</div>`,
    data() {
        return {
            pending: false,
            noMorePosts: false,
            scrollY: 0,
            debounceTimer: null,
            errorMsg: '',
            loadStatusMsg: '',
            postsPerPage: 10,
            signedIn: signedIn,
            feedType: feedType,
            feedPosts: [],
            header: document.querySelector('header'),
            footer: document.querySelector('footer'),
        }
    },
    watch: {
        errorMsg(current, _) {
            if (current) this.$nextTick(() => this.$refs.mainErrorMsg.scrollIntoView({behavior: 'smooth', block: 'end'}));
        },
    },
    methods: {
        getMorePosts() {
            this.pending = true;
            this.loadStatusMsg = 'Loading...';

            const url = `/network/morePosts/?posts=${this.feedPosts.length}&feedType=${this.feedType}`;

            fetch(url, {
                headers: {'X-Requested-With': 'XMLHttpRequest'}
            })
            .then(res => res.json())
            .then(data => {
                this.pending = false;

                if ('posts' in data) {
                    data.posts.forEach(post => this.feedPosts.push(post));

                    if (data.posts.length === 0) {
                        this.loadStatusMsg = 'No posts yet.';
                        this.noMorePosts = true;
                    }
                    else if (data.posts.length % 10 !== 0) {
                        this.loadStatusMsg = 'No more posts to load.';
                        this.noMorePosts = true;
                    }
                    else
                        this.loadStatusMsg = '';
                }
                else 
                    this.errorMsg = 'Problem loading posts. Try again later.';
            })
            .catch(err => console.log(err))
        },
        handleUpdate(updateType, info) {
            switch(updateType) {
                case 'error':
                    this.errorMsg = info.error;
                    break;
                default:
                    this.updatePost(updateType, info);
            }
        },
        updatePost(eventType, info) {
            const i = this.feedPosts.findIndex(p => p.id === info.id);
            switch(eventType) {
                case 'remove':
                    this.feedPosts.splice(i, 1);
                    if (!this.noMorePosts && this.feedPosts.length < 3) 
                        this.getMorePosts();
                    break;
                case 'edit':
                case 'like':
                    const post = this.feedPosts[i];
                    Object.entries(info).forEach(([key, value]) => post[key] = value);
                    break;
            }
        },
        addNewPost(post) {
            this.feedPosts.unshift(post);
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
        onScrollF() {
            const newScrollY = document.documentElement.scrollTop;
            const pageHeight = document.documentElement.offsetHeight;
            const windowHeight = window.innerHeight;

            if (newScrollY > windowHeight * 0.7)
                document.querySelector('#scrollUpBtn').classList.add('visible');
            else
                document.querySelector('#scrollUpBtn').classList.remove('visible');

            // load new posts
            if (!this.noMorePosts && !this.pending) {
                if (newScrollY > pageHeight - 2 * windowHeight) {
                    this.getMorePosts();
                }
            }

            if (newScrollY < this.scrollY)
            {
                this.header.classList.remove('invisible');
                this.footer.classList.remove('invisible');
            }
            else {
                this.header.classList.add('invisible');
                this.footer.classList.add('invisible');
            }

            if (newScrollY < 10) {
                this.header.classList.remove('invisible');
            }
            else if (newScrollY > pageHeight - windowHeight){
                this.footer.classList.remove('invisible');
            }

            this.scrollY = newScrollY;
        },
        handleScroll() {},
    },
    created() {
        this.getMorePosts();
        if (window.innerHeight > window.innerWidth) {
            this.handleScroll = () => {
                if (!this.debounceTimer) {
                    this.onScrollF();
                    this.debounceTimer = setTimeout(() => {
                        this.onScrollF();
                        this.debounceTimer = clearTimeout(this.debounceTimer);
                    }, 500);
                }  
            }
        }
        else {
            this.handleScroll = () => {
                if (!this.debounceTimer) {
                    this.debounceTimer = setTimeout(() => {
                        this.onScrollF();
                        this.debounceTimer = clearTimeout(this.debounceTimer);
                    }, 100);
                } 
            }
        }
    },
    mounted() {
        document.addEventListener('scroll', this.handleScroll);
    }

});

app.component('post-meta', {
    template: `<div class="post-meta">
    <form v-show="editVisible">
        <p v-show="editFormErrorMessage" class="error-msg">{{ editFormErrorMessage }}</p>
        <textarea name="text" v-model="editedPostText" required></textarea>
        <button type="submit" @click.prevent="savePost()">Save</button>
        <button type="button" @click="emitToggle('edit')">Cancel</button>
    </form>
    <div v-show="deleteVisible" class="post-meta">
        <div class="post-meta-msg">Are you sure you want to delete this post?</div>
        <button type="button" @click="deletePost()">Confirm</button>
        <button type="button" @click="emitToggle('delete')">Cancel</button>
    </div>
</div>`,
    props: ['post', 'editVisible', 'deleteVisible'],
    data() {
        return {
            editFormErrorMessage: '',
            editedPostText: '',
        }
    },
    mounted() {
        this.editFormErrorMessage = '';
        this.editedPostText = this.post.text;
    },
    methods: {
        emitToggle(btn) {
            this.$emit('toggle', btn);
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
            this.$emit('toggle', 'edit');
        },
        deletePost() {
            fetch('/network/deletePost/', {
                method: 'POST',
                headers: getAjaxHeaders(),
                body: JSON.stringify({postId: this.post.id})
            })
            .then(res => res.json())
            .then(data => {      
                if ('error' in data) this.$emit('update', 'error', {'error': data.error});
                else if ('ok' in data) this.$emit('update', 'remove', {id:this.post.id });
                else throw data;
            })
            .catch(err => console.log(err));
        },
    },
});

app.component('post-post', {
    template: `<div class="post-post">
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
        <button v-if="post.self" class="btn-sm" @click="emitToggle('edit')">Edit</button>
        <button v-if="post.self" class="btn-sm" @click="emitToggle('delete')">Delete</button>
    </div>
    <div class="post-body" v-html="post.text"></div>
    <div class="post-footer">
        <button v-if="isSignedIn" class="btn btn-likes" @click="like()">
            <div class="heart">
                <transition name="heart-liked">
                    <i v-if="post.liked" class="heart-liked"></i>
                </transition>
                <i class="heart-hollow"></i>
            </div>
            <span class="num-likes">{{ post.likes }}</span>
        </button>
        <button v-else class="btn btn-likes" disabled title="Sign in to leave likes">
            <div class="heart">
                <i class="heart-hollow"></i>
            </div>
            <span class="num-likes">{{ post.likes }}</span>
        </button>
    </div>
</div>`,
    props: ['post', 'isSignedIn'],
    methods: {
        getNetworkerUrl() {
            return `/network/user/${this.post.networkerId}/`;
        },
        emitToggle(btn) {
            this.$emit('toggle', btn);
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
    },

});

app.component('my-post', {
    template: `<transition name="post" mode="out-in">
    <post-post v-if="!metaVisible" :isSignedIn="true" :post="post" @toggle="toggle" @update="emitUpdate" />
    <post-meta v-else :post="post" :editVisible="editFormVisible" :deleteVisible="deleteConfirmationVisible" 
    @toggle="toggle" @update="emitUpdate" />
</transition>`,
    components: ['post-post', 'post-meta'],
    props: ['post'],
    data() {
        return {
            editFormVisible: false,
            deleteConfirmationVisible: false,
        }
    },
    computed: {
        metaVisible() {
            return this.editFormVisible || this.deleteConfirmationVisible
        }
    },
    methods: {
        toggle(btnName) { 
            switch(btnName) {
                case 'edit':
                    this.editFormVisible = ! this.editFormVisible;
                    break;
                case 'delete':
                    this.deleteConfirmationVisible = !this.deleteConfirmationVisible;
                    break;
            }       
        },
        emitUpdate(updateName, info) {
            this.$emit('update', updateName, info);
        }
    }
});

app.component('post', {
    template: `<div class="post">
    <my-post v-if="post.self" :post="post" @update="emitUpdate" />
    <post-post v-else :isSignedIn="isSignedIn()" :post="post" @update="emitUpdate" />
</div>`,
    props: ['post'],
    methods: {
        isSignedIn() {
            return signedIn;
        },
        emitUpdate(updateName, info) {
            this.$emit('update', updateName, info);
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