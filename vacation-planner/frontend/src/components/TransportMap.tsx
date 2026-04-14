"use client";

import { useEffect, useRef, useState } from "react";
import { MapContainer, TileLayer, Marker, Polyline, Popup, useMap } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

interface Coordinate { lat: number; lng: number; }
interface TransportLeg { mode: string; name: string; origin_coords: Coordinate; destination_coords: Coordinate; price: number; duration_minutes: number; polyline: string | null; }
interface ConsolidatedLogistics { total_price: number; currency: string; legs: TransportLeg[]; map_center: Coordinate; }

/**
 * Inner component that always runs inside <MapContainer>.
 * Re-fires fitBounds whenever `currentOption` reference changes so switching
 * Budget ↔ Premium ↔ Balanced zooms the map to the correct route.
 */
function MapViewController({ currentOption }: { currentOption: ConsolidatedLogistics }) {
  const map = useMap();

  useEffect(() => {
    const allCoords: [number, number][] = [];

    currentOption.legs.forEach((leg) => {
      // Collect every non-zero coordinate in this leg
      if (leg.origin_coords?.lat && leg.origin_coords?.lng)
        allCoords.push([leg.origin_coords.lat, leg.origin_coords.lng]);
      if (leg.destination_coords?.lat && leg.destination_coords?.lng)
        allCoords.push([leg.destination_coords.lat, leg.destination_coords.lng]);

      // Spread all road-curve points from the GeoJSON polyline (gives tightest bounds)
      if (leg.polyline) {
        try {
          const geoJson = JSON.parse(leg.polyline);
          if (geoJson?.coordinates) {
            // GeoJSON = [lng, lat] → Leaflet needs [lat, lng]
            geoJson.coordinates.forEach((c: [number, number]) =>
              allCoords.push([c[1], c[0]])
            );
          }
        } catch (_) {}
      }
    });

    if (allCoords.length > 1) {
      map.fitBounds(allCoords, { padding: [50, 50], maxZoom: 14 });
    } else {
      const c = currentOption.map_center;
      if (c?.lat && c?.lng) map.setView([c.lat, c.lng], 12);
    }
  // `currentOption` identity change triggers this (e.g. Budget → Premium)
  }, [currentOption, map]);

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

// OriginIcon  – green, departure city (✈ taking off)
const OriginIcon  = createCustomIcon("#22C55E", "🛫");
// AirportIcon – purple, arrival airport
const AirportIcon = createCustomIcon("#8A2BE2", "🛬");
// HotelIcon   – cyan, destination hotel / city centre
const HotelIcon   = createCustomIcon("#00F0FF", "🏨");

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

  // ── Derive polylines (GeoJSON [lng,lat] → Leaflet [lat,lng]) ──────────────
  const polylinesToDraw: { key: string; positions: [number, number][]; color: string; dashed: boolean }[] = [];

  // ── Derive markers with semantic icons ────────────────────────────────────
  // Use a Map so duplicate coordinates (airport leg shares coords with ground leg) are collapsed.
  const markerMap = new Map<string, { pos: [number, number]; icon: L.DivIcon; label: string }>();

  currentOption.legs.forEach((leg) => {
    // --- polyline ---
    if (leg.polyline) {
      try {
        const geoJSON = JSON.parse(leg.polyline);
        if (geoJSON.type === "LineString" && Array.isArray(geoJSON.coordinates)) {
          // GeoJSON = [lng, lat] → Leaflet needs [lat, lng]
          const latLngs: [number, number][] = geoJSON.coordinates.map(
            (c: [number, number]) => [c[1], c[0]]
          );
          polylinesToDraw.push({
            key: leg.mode,
            positions: latLngs,
            color: leg.mode === "uber" ? "#8A2BE2" : "#00F0FF",
            dashed: leg.mode === "bus" || leg.mode === "train",
          });
        }
      } catch (e) {
        console.error("Failed to parse polyline", e);
      }
    }

    // --- markers ---
    const isCoordValid = (c: Coordinate) =>
      c && !(c.lat === 0 && c.lng === 0) && c.lat !== undefined && c.lng !== undefined;

    if (isCoordValid(leg.origin_coords)) {
      const key = `${leg.origin_coords.lat.toFixed(4)},${leg.origin_coords.lng.toFixed(4)}`;
      if (!markerMap.has(key)) {
        // Flight origin = departure city; ground leg origin = arrival airport
        const icon = leg.mode === "flight" ? OriginIcon : AirportIcon;
        const label =
          leg.mode === "flight"
            ? "✈ Departure City"
            : `${leg.name} – Origin (Airport)`;
        markerMap.set(key, { pos: [leg.origin_coords.lat, leg.origin_coords.lng], icon, label });
      }
    }

    if (isCoordValid(leg.destination_coords)) {
      const key = `${leg.destination_coords.lat.toFixed(4)},${leg.destination_coords.lng.toFixed(4)}`;
      if (!markerMap.has(key)) {
        // Flight destination = arrival airport; ground leg destination = hotel/city
        const icon = leg.mode === "flight" ? AirportIcon : HotelIcon;
        const label =
          leg.mode === "flight"
            ? "🛬 Arrival Airport"
            : "🏨 Hotel / Destination";
        markerMap.set(key, { pos: [leg.destination_coords.lat, leg.destination_coords.lng], icon, label });
      }
    }
  });

  const uniqueMarkers = Array.from(markerMap.values());

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

      <MapContainer
        center={[center.lat || 0, center.lng || 0]}
        zoom={12}
        zoomControl={false}
        scrollWheelZoom={true}
        className="w-full h-full z-0 relative"
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          className="glass-tiles"
        />

        {/* Re-fits the map bounds whenever the selected transport tier changes */}
        <MapViewController currentOption={currentOption} />

        {/* Road-geometry polylines — keyed by mode so React properly diffs on tier switch */}
        {polylinesToDraw.map((line) => (
          <Polyline
            key={line.key}
            positions={line.positions}
            color={line.color}
            weight={4}
            opacity={0.85}
            dashArray={line.dashed ? "10, 8" : undefined}
          />
        ))}

        {/* Semantic markers: departure city, arrival airport, hotel */}
        {uniqueMarkers.map((m, idx) => (
          <Marker key={idx} position={m.pos} icon={m.icon}>
            <Popup>{m.label}</Popup>
          </Marker>
        ))}
      </MapContainer>
    </>
  );
}
