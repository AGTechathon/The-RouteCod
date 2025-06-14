import React from 'react';

const Reviews = () => {
  const reviews = [
    {
      name: 'Sarah Johnson',
      rating: 5,
      feedback: 'TripCraft made my trip easy and stress-free. The AI gave a solid plan I could quickly customize. Highly recommend it!',
    },
    {
      name: 'Rahul Sharma',
      rating: 4,
      feedback: 'The AI-generated itinerary was spot-on, covering all key spots and local food joints. The interface is user-friendly, though a few more adventure options would be great.',
    },
    {
      name: 'Emily Chen',
      rating: 5,
      feedback: 'I was amazed at how TripCraft’s AI tailored a Japan itinerary to my love for culture and food. The basic plan was perfect for a first-time visitor like me!',
    },
  ];

  const renderStars = (rating) => {
    return Array.from({ length: 5 }, (_, index) => (
      <span key={index} className={index < rating ? 'text-yellow-400' : 'text-gray-300'}>
        ★
      </span>
    ));
  };

  return (
    <section className="py-20 bg-gradient-to-b from-blue-50 to-white">
      <div className="container mx-auto px-4 w-[70%]">
        <h2 className="text-4xl md:text-5xl font-extrabold text-center text-gray-800 mb-12 animate-fade-in">
          What Travelers Say About TripCraft
        </h2>
        <p className="text-lg text-center text-gray-600 mb-16 max-w-2xl mx-auto">
          Hear from our users who explored the world with AI-powered itineraries.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {reviews.map((review, index) => (
            <div
              key={index}
              className="bg-white rounded-xl shadow-lg p-6 transform transition-all duration-500 hover:scale-105 hover:shadow-2xl"
            >
              <div className="flex mb-4">{renderStars(review.rating)}</div>
              <p className="text-gray-600 mb-4 italic">"{review.feedback}"</p>
              <h3 className="text-lg font-semibold text-gray-800 text-right">
                - {review.name}
              </h3>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Reviews;