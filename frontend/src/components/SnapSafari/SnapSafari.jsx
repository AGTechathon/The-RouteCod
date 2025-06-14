import React, { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';

const SnapSafari = () => {
  const [posts, setPosts] = useState([
    {
      id: 1,
      image: './img/bbg1.jpg',
      location: 'Santorini',
      date: 'June 10, 2025',
      description: 'Sunsets over the caldera were breathtaking! Loved this AI-planned gem.',
      likes: 342,
      comments: ['Amazing view!', 'Wish I was there!'],
    },
    {
      id: 2,
      image: './img/bbg2.jpg',
      location: 'Kyoto',
      date: 'June 8, 2025',
      description: 'Exploring temples with the AI plan was seamless. Cherry blossoms were amazing!',
      likes: 287,
      comments: ['Stunning shot!', 'Love the colors!'],
    },
    {
      id: 3,
      image: './img/bbg3.jpg',
      location: 'Machu Picchu',
      date: 'June 5, 2025',
      description: 'Hiked to the ruins with a perfect AI itinerary. Unforgettable!',
      likes: 198,
      comments: ['Epic adventure!', 'Incredible place!'],
    },
    {
      id: 4,
      image: './img/bbg4.jpg',
      location: 'Cape Town',
      date: 'June 3, 2025',
      description: 'Table Mountain views were stunning, thanks to AI suggestions.',
      likes: 156,
      comments: ['Wow, what a view!', 'Adding this to my list!'],
    },
  ]);

  const [selectedPost, setSelectedPost] = useState(null);
  const [newComment, setNewComment] = useState('');
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [selectedImage, setSelectedImage] = useState(null);
  const [caption, setCaption] = useState('');
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef(null);
  const commentSectionRef = useRef(null);

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file && file.type.startsWith('image/')) {
      setSelectedImage(file);
    } else {
      alert('Please select an image file.');
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
      setSelectedImage(file);
    } else {
      alert('Please drop an image file.');
    }
  };

  const handleImageSubmit = (e) => {
    e.preventDefault();
    if (selectedImage && caption.trim()) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setPosts([
          ...posts,
          {
            id: posts.length + 1,
            image: e.target.result,
            location: 'New Destination',
            date: new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' }),
            description: caption,
            likes: 0,
            comments: [],
          },
        ]);
        setSelectedImage(null);
        setCaption('');
        setShowUploadModal(false);
      };
      reader.readAsDataURL(selectedImage);
    }
  };

  const handleLike = (postId) => {
    setPosts(posts.map(post => 
      post.id === postId ? { ...post, likes: post.likes + 1 } : post
    ));
  };

  const handleCommentSubmit = (postId) => {
    if (newComment.trim()) {
      setPosts((prevPosts) =>
        prevPosts.map((post) =>
          post.id === postId
            ? { ...post, comments: [...post.comments, newComment] }
            : post
        )
      );
      setSelectedPost((prevSelectedPost) =>
        prevSelectedPost && prevSelectedPost.id === postId
          ? { ...prevSelectedPost, comments: [...prevSelectedPost.comments, newComment] }
          : prevSelectedPost
      );
      setNewComment('');
    }
  };

  const handleCommentKeyDown = (e, postId) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleCommentSubmit(postId);
    }
  };

  useEffect(() => {
    if (commentSectionRef.current) {
      commentSectionRef.current.scrollTop = commentSectionRef.current.scrollHeight;
    }
  }, [selectedPost?.comments]);

  return (
    <section className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4">
        {/* Simplified Profile Section: 30% Screen Height */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="h-[30vh] flex flex-col items-center justify-center bg-white rounded-xl shadow-md mb-12"
        >
          <img
            src="./img/profile.jpg"
            alt="Profile"
            className="w-16 h-16 rounded-full object-cover mb-2 border-2 border-blue-600"
          />
          <h2 className="text-2xl font-semibold text-gray-800 mb-1">Jane Doe</h2>
          <p className="text-base text-blue-600 mb-3">@JaneWanderer</p>
          <div className="flex space-x-6 text-gray-600 text-sm">
            <span>{posts.length} Posts</span>
            <span>1.2K Followers</span>
          </div>
        </motion.div>

        {/* Upload Button */}
        <div className="flex justify-center mb-8">
          <button
            onClick={() => setShowUploadModal(true)}
            className="bg-blue-600 text-white font-semibold py-4 px-4 rounded-full hover:bg-blue-700 transition-all duration-300"
          >
            <span className="text-xl">+</span> Add Photo
          </button>
        </div>

        {/* Image Grid: 3 Columns */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4, duration: 0.6 }}
          className="grid grid-cols-1 md:grid-cols-3 gap-4 w-[80%] mx-auto"
        >
          {posts.map((post) => (
            <div
              key={post.id}
              onClick={() => setSelectedPost(post)}
              className="relative bg-white rounded-xl shadow-lg overflow-hidden cursor-pointer group"
            >
              <img
                src={post.image}
                alt={post.location}
                className="w-full h-48 object-cover"
              />
              <div className="absolute inset-0 bg-black/50 bg-opacity-0 group-hover:bg-opacity-50 transition-all duration-300 flex items-center justify-center opacity-0 group-hover:opacity-100">
                <div className="text-white flex items-center space-x-6">
                  <div className="flex items-center space-x-2">
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" clipRule="evenodd" />
                    </svg>
                    <span>{post.likes}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M2 10.5a1.5 1.5 0 113 0v6a1.5 1.5 0 01-3 0v-6zM6 10.333v5.43a2 2 0 001.106 1.79l.05.025A4 4 0 008.943 18h5.416a2 2 0 001.962-1.608l1.2-6A2 2 0 0015.56 8H12V4a2 2 0 00-2-2 1 1 0 00-1 1v.667a4 4 0 01-.8 2.4L6.8 7.933a4 4 0 00-.8 2.4z" />
                    </svg>
                    <span>{post.comments.length}</span>
                  </div>
                </div>
              </div>
              <div className="p-3">
                <h3 className="text-sm font-semibold text-blue-600">{post.location}</h3>
                <p className="text-xs text-gray-500">{post.date}</p>
              </div>
            </div>
          ))}
        </motion.div>

        {/* Image Upload Modal */}
        {showUploadModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-md">
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="bg-white rounded-lg p-8 w-[90%] max-w-md"
            >
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-xl font-semibold text-gray-800">Share a Travel Moment</h3>
                <button
                  onClick={() => setShowUploadModal(false)}
                  className="text-gray-600 hover:text-gray-800"
                  aria-label="Close upload modal"
                >
                  ✕
                </button>
              </div>
              <form onSubmit={handleImageSubmit} className="space-y-6">
                <div
                  className={`border-2 border-dashed ${dragActive ? 'border-blue-600' : 'border-gray-300'} rounded-lg p-8 text-center cursor-pointer`}
                  onClick={() => fileInputRef.current?.click()}
                  onDragEnter={handleDrag}
                  onDragOver={handleDrag}
                  onDragLeave={handleDrag}
                  onDrop={handleDrop}
                >
                  {selectedImage ? (
                    <img
                      src={URL.createObjectURL(selectedImage)}
                      alt="Preview"
                      className="max-h-64 mx-auto rounded-lg"
                    />
                  ) : (
                    <div className="text-gray-500">
                      <p className="text-base mb-2">Click or drag to upload an image</p>
                      <p className="text-sm">Supported formats: JPG, PNG</p>
                    </div>
                  )}
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/*"
                    onChange={handleImageChange}
                    className="hidden"
                  />
                </div>
                <div>
                  <label htmlFor="caption" className="block text-sm font-medium text-gray-700 mb-2">
                    Caption
                  </label>
                  <textarea
                    id="caption"
                    value={caption}
                    onChange={(e) => setCaption(e.target.value)}
                    className="w-full bg-gray-50 text-gray-900 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-600"
                    rows="3"
                    placeholder="Describe your travel moment..."
                  />
                </div>
                <button
                  type="submit"
                  disabled={!selectedImage || !caption.trim()}
                  className="w-full bg-blue-600 text-white py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Share Post
                </button>
              </form>
            </motion.div>
          </div>
        )}

        {/* Post View Modal */}
        {selectedPost && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-md">
            <div className="bg-white rounded-xl shadow-2xl w-[80%] h-[60vh] flex overflow-hidden">
              {/* Post Image: 60% Width */}
              <div className="w-[60%]">
                <img
                  src={selectedPost.image}
                  alt={selectedPost.location}
                  className="w-full h-full object-cover"
                />
              </div>
              {/* Comments and Like: 40% Width */}
              <div className="w-[40%] p-4 flex flex-col">
                <div className="flex-1 overflow-hidden">
                  <h3 className="text-base font-semibold text-blue-600 mb-2">{selectedPost.location}</h3>
                  <p className="text-sm text-gray-500 mb-3 line-clamp-2">{selectedPost.description}</p>
                  <div ref={commentSectionRef} className="h-[calc(100%-5.8rem)] overflow-y-scroll">
                    {selectedPost

.comments.map((comment, index) => (
                      <p key={index} className="text-sm text-gray-500 mb-2 break-words">
                        @Doctor Strange: {comment}
                      </p>
                    ))}
                  </div>
                </div>
                <div className="mt-3">
                  <div className="flex items-center text-red-500 mb-3">
                    <button
                      onClick={() => handleLike(selectedPost.id)}
                      className="flex items-center"
                      aria-label="Like post"
                    >
                      <svg className="w-5 h-5 mr-1" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" clipRule="evenodd" />
                      </svg>
                      <span>{selectedPost.likes}</span>
                    </button>
                  </div>
                  <div className="flex">
                    <input
                      type="text"
                      value={newComment}
                      onChange={(e) => setNewComment(e.target.value)}
                      onKeyDown={(e) => handleCommentKeyDown(e, selectedPost.id)}
                      placeholder="Add a comment..."
                      className="flex-1 p-2 text-sm border border-gray-300 rounded-l-md focus:outline-none focus:ring-2 focus:ring-blue-600"
                      aria-label="Comment input"
                    />
                    <button
                      onClick={() => handleCommentSubmit(selectedPost.id)}
                      className="bg-blue-600 text-white px-4 py-2 rounded-r-md hover:bg-blue-700 hover:cursor-pointer"
                      aria-label="Submit comment"
                    >
                      Post
                    </button>
                  </div>
                </div>
              </div>
              <button
                onClick={() => setSelectedPost(null)}
                className="absolute top-4 right-4 text-white text-xl font-bold hover:cursor-pointer"
                aria-label="Close modal"
              >
                ✕
              </button>
            </div>
          </div>
        )}
      </div>
    </section>
  );
};

export default SnapSafari;