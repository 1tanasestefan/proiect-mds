import { useEffect, useState } from "react";
import { supabase } from "@/lib/supabase";

export interface OnlineUser {
  id: string;
  name: string;
  avatarId?: number; // deterministic avatar seed
}

export function useMultiplayer(itineraryId: string, currentUser: { id: string; email: string } | null, onDatabaseUpdate?: (payload: any) => void) {
  const [onlineUsers, setOnlineUsers] = useState<OnlineUser[]>([]);
  const [highlightedActivityId, setHighlightedActivityId] = useState<string | null>(null);
  const [channel, setChannel] = useState<any>(null);

  useEffect(() => {
    if (!supabase || !itineraryId || !currentUser) return;

    // Create unique room per itinerary
    const room = supabase.channel(`room_itinerary_${itineraryId}`);

    // Parse a user-friendly name from email
    const username = currentUser.email.split("@")[0];
    const avatarId = currentUser.email.length % 10; // stable arbitrary avatar seed

    // Set up presence
    room
      .on("presence", { event: "sync" }, () => {
        const state = room.presenceState();
        const users: OnlineUser[] = [];
        
        Object.keys(state).forEach((key) => {
          const presences = state[key] as any[];
          if (presences && presences.length > 0) {
            // Keep unique users by ID
            if (!users.some(u => u.id === presences[0].id)) {
              users.push({
                id: presences[0].id,
                name: presences[0].name,
                avatarId: presences[0].avatarId,
              });
            }
          }
        });
        
        setOnlineUsers(users);
      })
      .on("presence", { event: "join" }, ({ key, newPresences }) => {
         // optional: toast logs can go here
      })
      .on("presence", { event: "leave" }, ({ key, leftPresences }) => {
         // optional: toast logs can go here
      });

    // Set up broadcast listening for highlighted activities
    room.on("broadcast", { event: "highlight" }, (payload) => {
      const { activityId, userId } = payload.payload;
      // When a highlight comes in from another user, render it and auto-clear after 3s
      if (userId !== currentUser.id) {
         setHighlightedActivityId(activityId);
         setTimeout(() => {
            setHighlightedActivityId((prev) => (prev === activityId ? null : prev));
         }, 3000);
      }
    });

    // Set up Postgres Database Sync
    // Trigger when this particular itinerary gets an UPDATE in the public schema
    room.on(
      "postgres_changes",
      {
        event: "UPDATE",
        schema: "public",
        table: "itineraries",
        filter: `id=eq.${itineraryId}`,
      },
      (payload) => {
        if (onDatabaseUpdate) onDatabaseUpdate(payload.new);
      }
    );

    // Subscribe to channel and track self
    room.subscribe(async (status) => {
      if (status === "SUBSCRIBED") {
        await room.track({
          id: currentUser.id,
          name: username,
          avatarId: avatarId,
          onlineAt: new Date().toISOString(),
        });
      }
    });

    setChannel(room);

    return () => {
      // Cleanup channel on unmount
      room.untrack();
      room.unsubscribe();
      supabase?.removeChannel(room);
    };
  }, [itineraryId, currentUser?.id, currentUser?.email]);

  const broadcastActivityHighlight = (activityId: string) => {
    if (channel && currentUser) {
      channel.send({
        type: "broadcast",
        event: "highlight",
        payload: { activityId, userId: currentUser.id },
      });
      
      // Highlight locally as well
      setHighlightedActivityId(activityId);
      setTimeout(() => {
         setHighlightedActivityId((prev) => (prev === activityId ? null : prev));
      }, 3000);
    }
  };

  return {
    onlineUsers,
    highlightedActivityId,
    broadcastActivityHighlight,
  };
}
