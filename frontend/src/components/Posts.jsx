import React from 'react';

const Posts = () => {
  const posts = [
    {
      snapSafariId: '@WanderLad',
      location: 'Santorini',
      date: 'June 10, 2025',
      description: 'Sunsets over the caldera were breathtaking! Loved this AI-planned gem.',
      image: './img/bbg1.jpg',
      likes: 342,
    },
    {
      snapSafariId: '@GlobeTrotter22',
      location: 'Kyoto',
      date: 'June 8, 2025',
      description: 'Exploring temples with the AI plan was seamless. Cherry blossoms were amazing!',
      image: './img/bbg2.jpg',
      likes: 287,
    },
    {
      snapSafariId: '@AdventureSeeker',
      location: 'Machu Picchu',
      date: 'June 5, 2025',
      description: 'Hiked to the ruins with a perfect AI itinerary. Unforgettable!',
      image: './img/bbg3.jpg',
      likes: 198,
    },
    {
      snapSafariId: '@TravelVibes',
      location: 'Cape Town',
      date: 'June 3, 2025',
      description: 'Table Mountain views were stunning, thanks to AI suggestions.',
      image: './img/bbg4.jpg',
      likes: 156,
    },
  ];

  return (
    <section className="py-16 bg-gray-50">
      <div className="container mx-auto px-4 w-[80%]">
        <h2 className="text-3xl md:text-4xl font-extrabold text-center text-gray-800 mb-10 animate-fade-in">
          SnapSafari: Travel Moments
        </h2>
        <p className="text-base text-center text-gray-600 mb-12 max-w-lg mx-auto">
          Discover inspiring travel photos shared by our community on SnapSafari.
        </p>
        <div className="space-y-12">
          {/* Top Row: Larger Images, 80% Width */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 w-[80%] mx-auto">
            {posts.slice(0, 2).map((post, index) => (
              <div
                key={index}
                className="bg-white rounded-xl shadow-lg overflow-hidden transform transition-all duration-500 hover:scale-105 hover:shadow-2xl"
              >
                <img
                  src={post.image}
                  alt={post.location}
                  className="w-full h-56 object-cover"
                />
                <div className="p-4">
                  <div className="flex justify-between items-center mb-1">
                    <h3 className="text-base font-semibold text-blue-600">
                      {post.snapSafariId}
                    </h3>
                    <div className="flex items-center text-red-500">
                      <span className="mr-1 text-sm">{post.likes}</span>
                      <svg
                        className="w-4 h-4"
                        fill="currentColor"
                        viewBox="0 0 20 20"
                        xmlns="http://www.w3.org/2000/svg"
                      >
                        <path
                          fillRule="evenodd"
                          d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z"
                          clipRule="evenodd"
                        />
                      </svg>
                    </div>
                  </div>
                  <p className="text-gray-500 text-sm mb-1">{post.description}</p>
                  <p className="text-xs text-gray-500 text-right">{post.date}</p>
                </div>
              </div>
            ))}
          </div>
          {/* Bottom Row: Smaller Images, 60% Width */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-[60%] mx-auto">
            {posts.slice(2, 4).map((post, index) => (
              <div
                key={index}
                className="bg-white rounded-xl shadow-lg overflow-hidden transform transition-all duration-500 hover:scale-105 hover:shadow-2xl"
              >
                <img
                  src={post.image}
                  alt={post.location}
                  className="w-full h-40 object-cover"
                />
                <div className="p-3">
                  <div className="flex justify-between items-center mb-1">
                    <h3 className="text-sm font-semibold text-blue-600">
                      {post.snapSafariId}
                    </h3>
                    <div className="flex items-center text-red-500">
                      <span className="mr-1 text-xs">{post.likes}</span>
                      <svg
                        className="w-3 h-3"
                        fill="currentColor"
                        viewBox="0 0 20 20"
                        xmlns="http://www.w3.org/2000/svg"
                      >
                        <path
                          fillRule="evenodd"
                          d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z"
                          clipRule="evenodd"
                        />
                      </svg>
                    </div>
                  </div>
                  <p className="text-gray-500 text-xs mb-1">{post.description}</p>
                  <p className="text-xs text-gray-500 text-right">{post.date}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};

export default Posts;