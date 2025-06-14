package com.TripCraftProject.Services;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.TripCraftProject.Repository.DestinationRepository;
import com.TripCraftProject.model.Destination;

@Service
public class DestinationService {

    @Autowired
    private DestinationRepository destinationRepository;

    public void addTimeSlotToSpots(String destinationName, String timeSlot) {
        Destination destination = destinationRepository.findByDestination(destinationName);
        if (destination != null && destination.getSpots() != null) {
            for (Destination.Spot spot : destination.getSpots()) {
                spot.setTimeSlot(timeSlot);
            }
            destinationRepository.save(destination);
        }
    }
}
