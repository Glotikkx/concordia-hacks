import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import json
import os
from datetime import datetime
from pathlib import Path
from PIL import Image, ImageTk
import io
import base64

# Data storage file
DATA_FILE = "social_media_data.json"

class SocialMediaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("HabitHub - Social Media App")
        self.root.state('zoomed')
        self.root.configure(bg="#3f278a")
        
        self.current_user = None
        self.users = self.load_data()
        
        self.show_login_screen()
    
    def load_data(self):
        """Load user data from JSON file"""
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                try:
                    return json.load(f)
                except:
                    return {}
        return {}
    
    def save_data(self):
        """Save user data to JSON file"""
        with open(DATA_FILE, 'w') as f:
            json.dump(self.users, f, indent=4)
    
    def clear_window(self):
        """Clear all widgets from window"""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def show_login_screen(self):
        """Display login/signup screen"""
        self.clear_window()
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        
        title = ttk.Label(main_frame, text="HabitHub", font=("Arial", 32, "bold"))

        title.pack(pady=20)
        
        subtitle = ttk.Label(main_frame, font=("Arial", 12))
        subtitle.pack(pady=10)
        
        # Login section
        login_frame = ttk.LabelFrame(main_frame, text="Login", padding=20)
        login_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        ttk.Label(login_frame, text="Username:", font=("Arial", 10)).pack(anchor=tk.W, pady=5)
        login_username = ttk.Entry(login_frame, width=30)
        login_username.pack(anchor=tk.W, pady=5)
        
        ttk.Label(login_frame, text="Password:", font=("Arial", 10)).pack(anchor=tk.W, pady=5)
        login_password = ttk.Entry(login_frame, width=30, show="*")
        login_password.pack(anchor=tk.W, pady=5)
        
        def login():
            username = login_username.get().strip()
            password = login_password.get()
            
            if not username or not password:
                messagebox.showerror("Error", "Please fill in all fields")
                return
            
            if username in self.users and self.users[username]['password'] == password:
                self.current_user = username
                self.show_feed_screen()
            else:
                messagebox.showerror("Error", "Invalid username or password")
        
        ttk.Button(login_frame, text="Login", command=login).pack(pady=10)
        
        # Signup section
        signup_frame = ttk.LabelFrame(main_frame, text="Create Account", padding=20)
        signup_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        ttk.Label(signup_frame, text="New Username:", font=("Arial", 10)).pack(anchor=tk.W, pady=5)
        signup_username = ttk.Entry(signup_frame, width=30)
        signup_username.pack(anchor=tk.W, pady=5)
        
        ttk.Label(signup_frame, text="Bio:", font=("Arial", 10)).pack(anchor=tk.W, pady=5)
        signup_bio = ttk.Entry(signup_frame, width=30)
        signup_bio.pack(anchor=tk.W, pady=5)
        
        ttk.Label(signup_frame, text="Password:", font=("Arial", 10)).pack(anchor=tk.W, pady=5)
        signup_password = ttk.Entry(signup_frame, width=30, show="*")
        signup_password.pack(anchor=tk.W, pady=5)
        
        def signup():
            username = signup_username.get().strip()
            bio = signup_bio.get().strip()
            password = signup_password.get()
            
            if not username or not password:
                messagebox.showerror("Error", "Please fill in all fields")
                return
            
            if username in self.users:
                messagebox.showerror("Error", "Username already exists")
                return
            
            self.users[username] = {
                'password': password,
                'bio': bio,
                'followers': [],
                'following': [],
                'posts': [],
                'likes': []
            }
            self.save_data()
            messagebox.showinfo("Success", "Account created! Now login.")
            signup_username.delete(0, tk.END)
            signup_bio.delete(0, tk.END)
            signup_password.delete(0, tk.END)
        
        ttk.Button(signup_frame, text="Sign Up", command=signup).pack(pady=10)
    
    def show_feed_screen(self):
        """Display main feed screen"""
        self.clear_window()
        self.root.state('zoomed')


        
        # Top bar
        top_frame = ttk.Frame(self.root)
        top_frame.pack(fill=tk.X, padx=10, pady=10)
       
        
        ttk.Label(top_frame, text=f"Welcome, {self.current_user}!", font=("Arial", 14, "bold")).pack(side=tk.LEFT)
        ttk.Button(top_frame, text="Profile", command=self.show_profile).pack(side=tk.RIGHT, padx=5)
        ttk.Button(top_frame, text="Logout", command=self.logout).pack(side=tk.RIGHT, padx=5)
        
        # Notebook (tabs)
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Feed tab
        feed_frame = ttk.Frame(notebook)
        notebook.add(feed_frame, text="🏠 Feed")
        self.create_feed_tab(feed_frame)
        
        # Create post tab
        post_frame = ttk.Frame(notebook)
        notebook.add(post_frame, text="✍️ Create Post")
        self.create_post_tab(post_frame)
        
        # Friends tab
        friends_frame = ttk.Frame(notebook)
        notebook.add(friends_frame, text="👥 Friends")
        self.create_friends_tab(friends_frame)
        
        # Rankings tab
        rankings_frame = ttk.Frame(notebook)
        notebook.add(rankings_frame, text="🏆 Rankings")
        self.create_rankings_tab(rankings_frame)
        
        # Discover tab
        discover_frame = ttk.Frame(notebook)
        notebook.add(discover_frame, text="🔍 Discover")
        self.create_discover_tab(discover_frame)

        # Explore tab (ALL POSTS + TAGS)
        explore_frame = ttk.Frame(notebook)
        notebook.add(explore_frame, text="🌎 Explore")
        self.create_explore_tab(explore_frame)
    
    def create_feed_tab(self, parent):
        """Create the feed tab"""
        canvas = tk.Canvas(parent, bg="#1a1a1a", highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#1a1a1a")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="n")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Get posts from following + own posts
        all_posts = []
        for username in self.users[self.current_user]['following'] + [self.current_user]:
            if username in self.users:
                for post in self.users[username]['posts']:
                    all_posts.append((username, post))
        
        # Ensure posts without tags still work
        all_posts.sort(key=lambda x: x[1].get('timestamp', ''), reverse=True)
        
        if not all_posts:
            label = tk.Label(scrollable_frame, text="No posts yet. Follow someone!", font=("Arial", 12), bg="#1a1a1a", fg="white")
            label.pack(pady=20)
        
        for username, post in all_posts:
            self.create_post_widget(scrollable_frame, username, post)
    
    def create_post_widget(self, parent, username, post):
        self.root.state('zoomed')

        """Create a single post widget"""
        # Main post container - centered and wide
        post_frame = tk.Frame(parent, bg="#262626", relief=tk.FLAT)
        post_frame.pack(pady=10, padx=450, fill=tk.BOTH, expand=False)
        
        # Post header
        header = tk.Frame(post_frame, bg="#262626")
        header.pack(fill=tk.X, padx=15, pady=10)
        
        username_label = tk.Label(header, text=f"@{username}", font=("Arial", 11, "bold"), bg="#262626", fg="white")
        username_label.pack(anchor=tk.W)
        
        time_label = tk.Label(header, text=post.get('timestamp', ''), font=("Arial", 8), bg="#262626", fg="#888888")
        time_label.pack(anchor=tk.W)
        
        # Post image (if exists)
        if post.get('image'):
            try:
                image_data = base64.b64decode(post['image'])
                image = Image.open(io.BytesIO(image_data))
                # Resize to fit better while maintaining aspect ratio
                max_width = 550
                max_height = 550
                image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                img_label = tk.Label(post_frame, image=photo, bg="#262626")
                img_label.image = photo  # Keep a reference
                img_label.pack(padx=15, pady=10)
            except Exception as e:
                error_label = tk.Label(post_frame, text="[Image failed to load]", font=("Arial", 9), bg="#262626", fg="#888888")
                error_label.pack(padx=15, pady=10)
        
        # Post content
        if post.get('content'):
            content_frame = tk.Frame(post_frame, bg="#262626")
            content_frame.pack(fill=tk.X, padx=15, pady=5)
            
            content_label = tk.Label(content_frame, text=post['content'], font=("Arial", 10), bg="#262626", fg="white", wraplength=520, justify=tk.LEFT)
            content_label.pack(anchor=tk.W)
        
        # Tags display (if any)
        tags = post.get('tags', [])
        if tags:
            tags_frame = tk.Frame(post_frame, bg="#262626")
            tags_frame.pack(fill=tk.X, padx=15, pady=5)
            tk.Label(tags_frame, text="Tags:", font=("Arial", 9, "bold"), bg="#262626", fg="#bbbbbb").pack(side=tk.LEFT)
            for t in tags:
                lbl = tk.Label(tags_frame, text=t, font=("Arial", 9), bg="#333333", fg="white", padx=6, pady=2)
                lbl.pack(side=tk.LEFT, padx=4)
        
        # Post footer
        footer = tk.Frame(post_frame, bg="#262626")
        footer.pack(fill=tk.X, padx=15, pady=10)
        
        likes = len(post.get('likes', []))
        likes_label = tk.Label(footer, text=f"❤️ {likes} likes", font=("Arial", 9), bg="#262626", fg="white")
        likes_label.pack(side=tk.LEFT, padx=10)
        
        def like_post():
            if self.current_user not in post.get('likes', []):
                post.setdefault('likes', []).append(self.current_user)
                self.save_data()
                messagebox.showinfo("Success", "Post liked!")
                self.show_feed_screen()
            else:
                messagebox.showinfo("Info", "You already liked this post")
        
        like_button = tk.Button(footer, text="👍 Like", command=like_post, bg="#404040", fg="black", border=0, padx=15, pady=5, font=("Arial", 9))
        like_button.pack(side=tk.LEFT, padx=5)
        
        # Separator
        separator = tk.Frame(post_frame, height=1, bg="#404040")
        separator.pack(fill=tk.X, pady=10)
    
    def create_post_tab(self, parent):
        """Create the post creation tab"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        ttk.Label(frame, text="Share your positive habits!", font=("Arial", 12, "bold")).pack(pady=10)
        
        text_area = scrolledtext.ScrolledText(frame, height=8, width=50, font=("Arial", 10))
        text_area.pack(fill=tk.BOTH, expand=False, pady=10)
        
        # Image selection
        image_label = ttk.Label(frame, text="No image selected", font=("Arial", 9))
        image_label.pack(pady=5)
        
        self.selected_image = None
        
        def select_image():
            file_path = filedialog.askopenfilename(
                filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif *.bmp"), ("All files", "*.*")]
            )
            if file_path:
                self.selected_image = file_path
                image_label.config(text=f"✅ Image selected: {os.path.basename(file_path)}")
        
        ttk.Button(frame, text="📷 Add Image", command=select_image).pack(pady=5)
        
        def post():
            content = text_area.get("1.0", tk.END).strip()
            
            if not content and not self.selected_image:
                messagebox.showerror("Error", "Post cannot be empty. Add text or an image!")
                return
            
            new_post = {
                'content': content,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M"),
                'likes': [],
                'image': None,
                'tags': []
            }
            
            # Extract hashtags (case-insensitive, store lowercase)
            words = content.split()
            for w in words:
                if w.startswith("#") and len(w) > 1:
                    tag = w.lower()
                    if tag not in new_post['tags']:
                        new_post['tags'].append(tag)
            
            # Encode image if selected
            if self.selected_image:
                try:
                    with open(self.selected_image, 'rb') as img_file:
                        new_post['image'] = base64.b64encode(img_file.read()).decode('utf-8')
                except:
                    messagebox.showerror("Error", "Could not load image")
                    return
            
            # Insert at front of user's posts
            self.users[self.current_user].setdefault('posts', []).insert(0, new_post)
            self.save_data()
            messagebox.showinfo("Success", "Post published!")
            text_area.delete("1.0", tk.END)
            image_label.config(text="No image selected")
            self.selected_image = None
            self.show_feed_screen()
        
        ttk.Button(frame, text="📤 Post", command=post).pack(pady=10)
    
    def create_friends_tab(self, parent):
        """Create the friends tab showing who you follow"""
        self.root.state('zoomed')


        canvas = tk.Canvas(parent, bg="gray", highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="gray")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="n")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        title = tk.Label(scrollable_frame, text="👥 Your Friends", font=("Arial", 16, "bold"), bg="#1a1a1a", fg="white")
        title.pack(pady=15)
        
        following_list = self.users[self.current_user].get('following', [])
        
        if not following_list:
            label = tk.Label(scrollable_frame, text="You haven't followed anyone yet!", font=("Arial", 11), bg="#1a1a1a", fg="white")
            label.pack(pady=20)
        
        for username in sorted(following_list):
            if username in self.users:
                friend_frame = tk.Frame(scrollable_frame, bg="#262626", relief=tk.FLAT)
                friend_frame.pack(pady=50, padx=650, fill=tk.X)
                
                name_label = tk.Label(friend_frame, text=f"@{username}", font=("Arial", 12, "bold"), bg="#262626", fg="white")
                name_label.pack(anchor=tk.W, padx=15, pady=(10, 5))
                
                bio_text = self.users[username].get('bio', '') if self.users[username].get('bio', '') else "(No bio)"
                bio_label = tk.Label(friend_frame, text=bio_text, font=("Arial", 9), bg="#262626", fg="#888888")
                bio_label.pack(anchor=tk.W, padx=15, pady=(0, 5))
                
                posts_count = len(self.users[username].get('posts', []))
                followers_count = len(self.users[username].get('followers', []))
                stats_label = tk.Label(friend_frame, text=f"📝 {posts_count} posts • 👥 {followers_count} followers", font=("Arial", 8), bg="#262626", fg="#888888")
                stats_label.pack(anchor=tk.W, padx=15, pady=(0, 10))
                
                def unfollow(u=username):
                    if u in self.users[self.current_user].get('following', []):
                        try:
                            self.users[self.current_user]['following'].remove(u)
                        except:
                            pass
                    if self.current_user in self.users[u].get('followers', []):
                        try:
                            self.users[u]['followers'].remove(self.current_user)
                        except:
                            pass
                    self.save_data()
                    self.show_feed_screen()
                
                btn = tk.Button(friend_frame, text="Unfollow ✕", command=unfollow, bg="#404040", fg="black", border=0, padx=15, pady=8, font=("Arial", 9))
                btn.pack(anchor=tk.W, padx=15, pady=(0, 10))
    
    def create_rankings_tab(self, parent):
        """Create the rankings/leaderboard tab"""
               
        self.root.state('zoomed')

        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(frame, text="🏆 Global Rankings", font=("Arial", 14, "bold")).pack(pady=10)
        ttk.Label(frame, text="Ranked by number of posts", font=("Arial", 10)).pack(pady=5)
        
        scroll_frame = ttk.Frame(frame)
        scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(scroll_frame, bg="gray", highlightthickness=0)
        scrollbar = ttk.Scrollbar(scroll_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Get all users with posts and sort by post count
        user_rankings = []
        for username, user_data in self.users.items():
            post_count = len(user_data.get('posts', []))
            if post_count > 0:  # Only include users with at least 1 post
                user_rankings.append((username, post_count))
        
        # Sort by post count (descending)
        user_rankings.sort(key=lambda x: x[1], reverse=True)
        
        if not user_rankings:
            ttk.Label(scrollable_frame, text="No posts yet! Be the first to post.", font=("Arial", 11)).pack(pady=20)
        else:
            for rank, (username, post_count) in enumerate(user_rankings, 1):
                # Highlight current user's friends in blue
                is_friend = username in self.users[self.current_user].get('following', [])
                is_self = username == self.current_user
                
                if is_self or is_friend:
                    rank_frame = ttk.Frame(scrollable_frame, relief=tk.RAISED, borderwidth=2)
                else:
                    rank_frame = ttk.Frame(scrollable_frame)
                
                rank_frame.pack(fill=tk.X, padx=5, pady=3)
                
                # Create a container for the rank info
                info_frame = ttk.Frame(rank_frame)
                info_frame.pack(fill=tk.X, padx=10, pady=8)
                
                # Medal emojis for top 3
                medal = ""
                if rank == 1:
                    medal = "🥇 "
                elif rank == 2:
                    medal = "🥈 "
                elif rank == 3:
                    medal = "🥉 "
                
                rank_text = f"#{rank} {medal}@{username}"
                
                if is_self:
                    rank_text += " (YOU)"
                
                # Rank and username (left side)
                ttk.Label(
                    info_frame,
                    text=rank_text,
                    font=("Arial", 11, "bold")
                ).pack(side=tk.LEFT, padx=5)
                
                # Post count (right side)
                ttk.Label(
                    info_frame,
                    text=f"📝 {post_count} posts",
                    font=("Arial", 10)
                ).pack(side=tk.RIGHT, padx=5)
                
                # Bio (second line)
                bio_text = self.users[username].get('bio', '') if self.users[username].get('bio', '') else "(No bio)"
                ttk.Label(
                    rank_frame,
                    text=bio_text,
                    font=("Arial", 8, "italic"),
                    foreground="gray"
                ).pack(fill=tk.X, padx=15)
    
    def create_discover_tab(self, parent):
        """Create the discover tab to find and follow users"""
        self.root.state('zoomed')

        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=300, pady=50)
        
        ttk.Label(frame, text="🔍 Discover Users", font=("Arial", 14, "bold")).pack(pady=10)
        
        scroll_frame = ttk.Frame(frame)
        scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(scroll_frame, bg="#9e89c4", highlightthickness=0)
        scrollbar = ttk.Scrollbar(scroll_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        user_count = 0
        for username in sorted(self.users.keys()):
            if username == self.current_user:
                continue
            
            user_count += 1
            user_frame = ttk.LabelFrame(scrollable_frame, text=f"@{username}", padding=50)
            user_frame.pack(fill=tk.X, padx=5, pady=5)
            
            bio_text = self.users[username].get('bio', '') if self.users[username].get('bio', '') else "(No bio)"
            ttk.Label(user_frame, text=bio_text, font=("Arial", 12)).pack(anchor=tk.W)
            
            stats = f"Posts: {len(self.users[username].get('posts', []))} | Followers: {len(self.users[username].get('followers', []))}"
            ttk.Label(user_frame, text=stats, font=("Arial", 9, "italic")).pack(anchor=tk.W, pady=3)
            
            is_following = username in self.users[self.current_user].get('following', [])
            
            
            def toggle_follow(u=username, following=is_following):
                if following:
                    self.users[self.current_user]['following'].remove(u)
                    self.users[u]['followers'].remove(self.current_user)
                else:
                    self.users[self.current_user]['following'].append(u)
                    self.users[u]['followers'].append(self.current_user)

                self.save_data()

                # ❗ Instead of creating a NEW Discover section,
                #    clear the existing one and rebuild it
                for widget in parent.winfo_children():
                    widget.destroy()

                self.create_discover_tab(parent)

            
            btn_text = "Unfollow ✓" if is_following else "Follow +"
            ttk.Button(user_frame, text=btn_text, command=toggle_follow).pack(anchor=tk.W, pady=5)
        
        if user_count == 0:
            ttk.Label(scrollable_frame, text="No other users yet!", font=("Arial", 11)).pack(pady=20)
    
    def create_explore_tab(self, parent):
        """Explore tab shows all posts + tag categories"""
        self.root.state('zoomed')


        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True)

        # ----------- TAB 1: ALL POSTS -------------
        all_tab = ttk.Frame(notebook)
        notebook.add(all_tab, text="🔥 All Posts")
        self.build_explore_feed(all_tab, mode="all")

        # ----------- TAB 2: #study ---------------
        study_tab = ttk.Frame(notebook)
        notebook.add(study_tab, text="#study")
        self.build_explore_feed(study_tab, mode="#study")

        # ----------- TAB 3: #hydrated ------------
        hydrated_tab = ttk.Frame(notebook)
        notebook.add(hydrated_tab, text="#hydrated")
        self.build_explore_feed(hydrated_tab, mode="#hydrated")

        # ----------- TAB 4: #nutrition -----------
        nutrition_tab = ttk.Frame(notebook)
        notebook.add(nutrition_tab, text="#nutrition")
        self.build_explore_feed(nutrition_tab, mode="#nutrition")
        
        # ----------- TAB 5: #fitness -----------
        fitness_tab = ttk.Frame(notebook)
        notebook.add(fitness_tab, text="#fitness")
        self.build_explore_feed(fitness_tab, mode="#fitness")
        
        # ----------- TAB 5: #sleep -----------
        fitness_tab = ttk.Frame(notebook)
        notebook.add(fitness_tab, text="#sleep")
        self.build_explore_feed(fitness_tab, mode="#sleep")


    
    def build_explore_feed(self, parent, mode="all"):
        canvas = tk.Canvas(parent, bg="#1a1a1a", highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#1a1a1a")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Gather *all* posts from *all* users
        all_posts = []
        for user, data in self.users.items():
            for post in data.get("posts", []):
                all_posts.append((user, post))

        # Filter by tag if needed
        if mode != "all":
            tag = mode.lower()
            all_posts = [
                (u, p) for (u, p) in all_posts
                if "tags" in p and tag in [t.lower() for t in p.get("tags", [])]
            ]

        # Sort newest first (by timestamp if present)
        all_posts.sort(key=lambda x: x[1].get("timestamp", ""), reverse=True)

        if not all_posts:
            msg = f"No posts found for {mode}" if mode != "all" else "No posts yet!"
            tk.Label(scrollable_frame, text=msg, fg="white", bg="#1a1a1a",
                     font=("Arial", 12)).pack(pady=20)
            return

        for username, post in all_posts:
            self.create_post_widget(scrollable_frame, username, post)
    
    def show_profile(self):
        """Show user profile"""
        profile_window = tk.Toplevel(self.root)
        profile_window.title(f"{self.current_user} - Profile")
        profile_window.geometry("1500x1200+750+600")
        profile_window.state('zoomed')  # Maximize window
        profile_window.configure(bg="#1a1a1a")
        
        # Main scrollable frame
        canvas = tk.Canvas(profile_window, bg="#1a1a1a", highlightthickness=0)
        scrollbar = ttk.Scrollbar(profile_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#1a1a1a")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="n")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Center wrapper for all content - takes 80% of screen width
        center_frame = tk.Frame(scrollable_frame, bg="#1a1a1a")
        center_frame.pack(fill=tk.BOTH, expand=True, pady=40, padx=550)
        
        # Header section
        header_frame = tk.Frame(center_frame, bg="#1a1a1a")
        header_frame.pack(fill=tk.X)
        
        username_label = tk.Label(header_frame, text=f"@{self.current_user}", font=("Arial", 32, "bold"), bg="#1a1a1a", fg="white")
        username_label.pack(pady=15)
        
        bio_label = tk.Label(header_frame, text=f"{self.users[self.current_user].get('bio', '')}", font=("Arial", 14), bg="#1a1a1a", fg="#888888")
        bio_label.pack(pady=8)
        
        # Stats section
        stats_frame = tk.Frame(center_frame, bg="#262626", relief=tk.FLAT)
        stats_frame.pack(fill=tk.X, pady=20)
        
        followers = len(self.users[self.current_user].get('followers', []))
        following = len(self.users[self.current_user].get('following', []))
        posts = len(self.users[self.current_user].get('posts', []))
        
        stats_label = tk.Label(stats_frame, text=f"📝 {posts} Posts     👥 {followers} Followers     🔗 {following} Following", font=("Arial", 15, "bold"), bg="#262626", fg="white")
        stats_label.pack(pady=25)
        
        # Followers section
        followers_label = tk.Label(center_frame, text="👥 Followers", font=("Arial", 16, "bold"), bg="#1a1a1a", fg="white")
        followers_label.pack(pady=(20, 15))
        
        if not self.users[self.current_user].get('followers', []):
            no_followers = tk.Label(center_frame, text="No followers yet", font=("Arial", 12), bg="#1a1a1a", fg="#888888")
            no_followers.pack()
        else:
            followers_display = tk.Frame(center_frame, bg="#1a1a1a")
            followers_display.pack(fill=tk.X)
            for follower in sorted(self.users[self.current_user].get('followers', [])):
                follower_label = tk.Label(followers_display, text=f"• @{follower}", font=("Arial", 13), bg="#1a1a1a", fg="white")
                follower_label.pack(pady=4)
        
        # Following section
        following_label = tk.Label(center_frame, text="🔗 Following", font=("Arial", 16, "bold"), bg="#1a1a1a", fg="white")
        following_label.pack(pady=(20, 15))
        
        if not self.users[self.current_user].get('following', []):
            no_following = tk.Label(center_frame, text="Not following anyone yet", font=("Arial", 12), bg="#1a1a1a", fg="#888888")
            no_following.pack()
        else:
            following_display = tk.Frame(center_frame, bg="#1a1a1a")
            following_display.pack(fill=tk.X)
            for person in sorted(self.users[self.current_user].get('following', [])):
                person_label = tk.Label(following_display, text=f"• @{person}", font=("Arial", 13), bg="#1a1a1a", fg="white")
                person_label.pack(pady=4)
        
        # Posts section
        posts_title = tk.Label(center_frame, text="📝 Your Posts", font=("Arial", 16, "bold"), bg="#1a1a1a", fg="white")
        posts_title.pack(pady=(20, 15))
        
        if not self.users[self.current_user].get('posts', []):
            no_posts = tk.Label(center_frame, text="No posts yet", font=("Arial", 12), bg="#1a1a1a", fg="#888888")
            no_posts.pack()
        else:
            posts_display = tk.Frame(center_frame, bg="#1a1a1a")
            posts_display.pack(fill=tk.BOTH, expand=True)
            for post in self.users[self.current_user].get('posts', []):
                post_card = tk.Frame(posts_display, bg="#262626", relief=tk.FLAT)
                post_card.pack(fill=tk.X, pady=10)
                
                time_label = tk.Label(post_card, text=post.get('timestamp', ''), font=("Arial", 11), bg="#262626", fg="#888888")
                time_label.pack(anchor=tk.W, padx=20, pady=(12, 5))
                
                content_label = tk.Label(post_card, text=post.get('content', ''), font=("Arial", 12), bg="#262626", fg="white", wraplength=800, justify=tk.CENTER)
                content_label.pack(anchor=tk.CENTER, padx=20, pady=(5, 15))
    
    def logout(self):
        """Logout user"""
        self.current_user = None
        self.show_login_screen()

if __name__ == "__main__":
    root = tk.Tk()
    app = SocialMediaApp(root)
    root.mainloop()