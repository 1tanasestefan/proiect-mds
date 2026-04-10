"use client";

import { useEffect, useState } from "react";
import { MapContainer, TileLayer, Marker, Polyline, Popup, useMap } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
interface Coordinate { lat: number; lng: number; }
interface TransportLeg { mode: string; name: string; origin_coords: Coordinate; destination_coords: Coordinate; price: number; duration_minutes: number; polyline: string | null; }
interface ConsolidatedLogistics { total_price: number; currency: string; legs: TransportLeg[]; map_center: Coordinate; }
// Map center controller component
function MapCenterController({ center, legs }: { center: {lat: number, lng: number}, legs: any[] }) {
  const map = useMap();
  useEffect(() => {
    if (center && center.lat && center.lng) {
      // Create a bounding box if we have polylines
      const allCoords: [number, number][] = [];
      legs.forEach(leg => {
         if (leg.origin_coords?.lat) allCoords.push([leg.origin_coords.lat, leg.origin_coords.lng]);
         if (leg.destination_coords?.lat) allCoords.push([leg.destination_coords.lat, leg.destination_coords.lng]);
         if (leg.polyline) {
             try {
                 const geoJson = JSON.parse(leg.polyline);
                 if (geoJson && geoJson.coordinates) {
                     geoJson.coordinates.forEach((c: any) => allCoords.push([c[1], c[0]]));
                 }
             } catch (e) {}
         }
      });
      
      if (allCoords.length > 0) {
          map.fitBounds(allCoords, { padding: [50, 50], maxZoom: 14 });
      } else {
          map.setView([center.lat, center.lng], 12);
      }
    }
  }, [center, legs, map]);
  return null;
}

// Custom markers using CSS to avoid external image loading issues
const createCustomIcon = (color: string, emoji: string) => {
  return L.divIcon({
    className: "custom-leaflet-icon",
    html: `<div style="
      background: ${color}; 
      width: 32px; 
      height: 32px; 
      border-radius: 50%; 
      display: flex; 
      align-items: center; 
      justify-content: center; 
      font-size: 16px; 
      box-shadow: 0 0 15px ${color}80;
      border: 2px solid white;
    ">${emoji}</div>`,
    iconSize: [32, 32],
    iconAnchor: [16, 16],
  });
};

const AirportIcon = createCustomIcon("#8A2BE2", "✈️");
const CityIcon = createCustomIcon("#00F0FF", "🏨");

interface Props {
  currentOption: ConsolidatedLogistics;
}

export default function TransportMap({ currentOption }: Props) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return null;

  const center = currentOption.map_center;
  const mapProps = {
    center: [center.lat || 0, center.lng || 0] as [number, number],
    zoom: 12,
    zoomControl: false,
    className: "w-full h-full z-0 relative", // Reset z-index
  };

  // Parse polylines from the legs
  const polylinesToDraw: { positions: [number, number][], color: string }[] = [];
  
  // Also collect distinct markers
  const markers: { pos: [number, number], icon: L.DivIcon, label: string }[] = [];

  currentOption.legs.forEach(leg => {
    if (leg.polyline) {
      try {
        const geoJSON = JSON.parse(leg.polyline);
        if (geoJSON.type === 'LineString') {
          // GeoJSON is [lon, lat], Leaflet is [lat, lon]
          const latLngs: [number, number][] = geoJSON.coordinates.map((c: any[]) => [c[1], c[0]]);
          polylinesToDraw.push({
             positions: latLngs,
             color: leg.mode === 'uber' ? '#8A2BE2' : '#00F0FF'
          });
        }
      } catch (e) {
        console.error("Failed to parse polyline", e);
      }
    }
    
    // Attempt to drop markers
    if (leg.origin_coords && leg.origin_coords.lat !== 0) {
        // Assume first major non-zero origin is airport
        markers.push({ 
           pos: [leg.origin_coords.lat, leg.origin_coords.lng], 
           icon: AirportIcon,
           label: leg.name + ' Origin'
        });
    }
    if (leg.destination_coords && leg.destination_coords.lat !== 0) {
        markers.push({ 
           pos: [leg.destination_coords.lat, leg.destination_coords.lng], 
           icon: CityIcon,
           label: 'Destination / Hotel'
        });
    }
  });

  // Deduplicate markers roughly based on lat/lng string
  const uniqueMarkers = Array.from(new Map(markers.map(m => [`${m.pos[0]},${m.pos[1]}`, m])).values());

  return (
    <>
      <style>{`
        /* Global Leaflet Dark Mode Inversion */
        .glass-tiles {
          filter: invert(100%) hue-rotate(180deg) brightness(95%) contrast(90%);
        }
        .leaflet-container {
          background: #0A0A0A;
          font-family: 'Inter', sans-serif;
        }
        /* Fix the attribution link colors in dark mode */
        .leaflet-control-attribution a {
          color: #00F0FF !important;
        }
        /* Custom map tooltips */
        .leaflet-popup-content-wrapper {
          background: rgba(10, 10, 10, 0.9);
          backdrop-filter: blur(10px);
          border: 1px solid rgba(255,255,255,0.1);
          color: white;
          border-radius: 12px;
        }
        .leaflet-popup-tip {
          background: rgba(10, 10, 10, 0.9);
        }
      `}</style>

      <MapContainer {...mapProps} scrollWheelZoom={false}>
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          className="glass-tiles"
        />
        
        <MapCenterController center={center} legs={currentOption.legs} />
        
        {polylinesToDraw.map((line, idx) => (
          <Polyline 
            key={idx} 
            positions={line.positions} 
            color={line.color} 
            weight={4}
            opacity={0.8}
            dashArray={idx > 0 && line.color === '#00F0FF' ? "10, 10" : undefined} // Give bus/train a dashed look if applicable
          />
        ))}

        {uniqueMarkers.map((m, idx) => (
           <Marker key={idx} position={m.pos} icon={m.icon}>
               <Popup>{m.label}</Popup>
           </Marker>
        ))}

      </MapContainer>
    </>
  );
}
