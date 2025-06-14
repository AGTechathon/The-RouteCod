package com.TripCraftProject.Services;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.TripCraftProject.Repository.TripRepository;
import com.TripCraftProject.model.Trip;


@Service
public class TripService {

	@Autowired
    private  TripRepository tripRepository;
	
	public List<Trip> getTripsForLoggedInUser(String email) {
	    return tripRepository.findTripsSharedWithUser(email);
	}

}
