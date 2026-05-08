-- ═══════════════════════════════════════════════════════════════
-- AI Travel Planner - Supabase Schema
-- Run this in the Supabase SQL Editor (supabase.com → SQL Editor)
-- ═══════════════════════════════════════════════════════════════

-- ┌─────────────────────────────────────────────────────────────┐
-- │  1. PROFILES                                               │
-- │  Auto-created when a user registers via Supabase Auth      │
-- └─────────────────────────────────────────────────────────────┘

CREATE TABLE IF NOT EXISTS public.profiles (
    id          UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email       TEXT,
    display_name TEXT,
    avatar_url  TEXT,
    created_at  TIMESTAMPTZ DEFAULT now()
);

-- Trigger: auto-create profile on user signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, email, display_name)
    VALUES (
        NEW.id,
        NEW.email,
        COALESCE(NEW.raw_user_meta_data ->> 'display_name', split_part(NEW.email, '@', 1))
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_new_user();


-- ┌─────────────────────────────────────────────────────────────┐
-- │  2. ITINERARIES                                            │
-- │  Stores the full FinalTripPlan JSON in a JSONB column      │
-- └─────────────────────────────────────────────────────────────┘

CREATE TABLE IF NOT EXISTS public.itineraries (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    title       TEXT NOT NULL,
    destination TEXT NOT NULL,
    start_date  DATE,
    end_date    DATE,
    is_public   BOOLEAN DEFAULT false,
    likes_count INT DEFAULT 0,
    forks_count INT DEFAULT 0,
    ai_data     JSONB NOT NULL,
    created_at  TIMESTAMPTZ DEFAULT now(),
    updated_at  TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_itineraries_user_id ON public.itineraries(user_id);
CREATE INDEX IF NOT EXISTS idx_itineraries_is_public ON public.itineraries(is_public);


-- ┌─────────────────────────────────────────────────────────────┐
-- │  3. ITINERARY LIKES                                        │
-- │  Prevents double-liking via composite primary key          │
-- └─────────────────────────────────────────────────────────────┘

CREATE TABLE IF NOT EXISTS public.itinerary_likes (
    user_id      UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    itinerary_id UUID NOT NULL REFERENCES public.itineraries(id) ON DELETE CASCADE,
    created_at   TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (user_id, itinerary_id)
);

CREATE INDEX IF NOT EXISTS idx_likes_itinerary_id ON public.itinerary_likes(itinerary_id);


-- ┌─────────────────────────────────────────────────────────────┐
-- │  4. TRIP COLLABORATORS                                     │
-- │  Real shared access for private itinerary collaboration     │
-- └─────────────────────────────────────────────────────────────┘

CREATE TABLE IF NOT EXISTS public.trip_collaborators (
    itinerary_id UUID NOT NULL REFERENCES public.itineraries(id) ON DELETE CASCADE,
    user_id      UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    role         TEXT NOT NULL CHECK (role IN ('viewer', 'editor')),
    invited_by   UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
    joined_at    TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (itinerary_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_trip_collaborators_user_id ON public.trip_collaborators(user_id);


-- ┌─────────────────────────────────────────────────────────────┐
-- │  5. TRIP INVITES                                           │
-- │  Expiring invite tokens that create collaborator records    │
-- └─────────────────────────────────────────────────────────────┘

CREATE TABLE IF NOT EXISTS public.trip_invites (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    itinerary_id UUID NOT NULL REFERENCES public.itineraries(id) ON DELETE CASCADE,
    token        TEXT NOT NULL UNIQUE,
    role         TEXT NOT NULL CHECK (role IN ('viewer', 'editor')),
    created_by   UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    expires_at   TIMESTAMPTZ NOT NULL,
    accepted_at  TIMESTAMPTZ,
    created_at   TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_trip_invites_itinerary_id ON public.trip_invites(itinerary_id);
CREATE INDEX IF NOT EXISTS idx_trip_invites_token ON public.trip_invites(token);


-- ┌─────────────────────────────────────────────────────────────┐
-- │  6. ACTIVITY VOTES                                         │
-- │  Persistent per-user votes for activity regeneration        │
-- └─────────────────────────────────────────────────────────────┘

CREATE TABLE IF NOT EXISTS public.activity_votes (
    itinerary_id    UUID NOT NULL REFERENCES public.itineraries(id) ON DELETE CASCADE,
    day_index       INT NOT NULL,
    activity_index  INT NOT NULL,
    user_id         UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    voter_name      TEXT NOT NULL,
    voter_avatar_id INT,
    created_at      TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (itinerary_id, day_index, activity_index, user_id)
);

CREATE INDEX IF NOT EXISTS idx_activity_votes_itinerary_id ON public.activity_votes(itinerary_id);


-- ┌─────────────────────────────────────────────────────────────┐
-- │  7. COLLECTIONS (folders / wishlists)                      │
-- └─────────────────────────────────────────────────────────────┘

CREATE TABLE IF NOT EXISTS public.collections (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    name        TEXT NOT NULL,
    description TEXT DEFAULT '',
    created_at  TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_collections_user_id ON public.collections(user_id);


-- ┌─────────────────────────────────────────────────────────────┐
-- │  8. COLLECTION ↔ ITINERARY (many-to-many join)             │
-- └─────────────────────────────────────────────────────────────┘

CREATE TABLE IF NOT EXISTS public.collection_itineraries (
    collection_id UUID NOT NULL REFERENCES public.collections(id) ON DELETE CASCADE,
    itinerary_id  UUID NOT NULL REFERENCES public.itineraries(id) ON DELETE CASCADE,
    added_at      TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (collection_id, itinerary_id)
);


-- ═══════════════════════════════════════════════════════════════
-- ROW LEVEL SECURITY (RLS)
-- Users can only access their own data
-- ═══════════════════════════════════════════════════════════════

-- Profiles
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own profile"
    ON public.profiles FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
    ON public.profiles FOR UPDATE
    USING (auth.uid() = id);

-- Itineraries
ALTER TABLE public.itineraries ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own itineraries"
    ON public.itineraries FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own itineraries"
    ON public.itineraries FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own itineraries"
    ON public.itineraries FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own itineraries"
    ON public.itineraries FOR DELETE
    USING (auth.uid() = user_id);

CREATE POLICY "Anyone can view public itineraries"
    ON public.itineraries FOR SELECT
    USING (is_public = true);

CREATE POLICY "Collaborators can view shared itineraries"
    ON public.itineraries FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.trip_collaborators
            WHERE itinerary_id = id AND user_id = auth.uid()
        )
    );

CREATE POLICY "Editors can update shared itineraries"
    ON public.itineraries FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM public.trip_collaborators
            WHERE itinerary_id = id AND user_id = auth.uid() AND role = 'editor'
        )
    );

-- Collections
ALTER TABLE public.collections ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own collections"
    ON public.collections FOR ALL
    USING (auth.uid() = user_id);

-- Collection-Itineraries join
ALTER TABLE public.collection_itineraries ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own collection items"
    ON public.collection_itineraries FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM public.collections
            WHERE id = collection_id AND user_id = auth.uid()
        )
    );

-- Itinerary Likes
ALTER TABLE public.itinerary_likes ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can like itineraries"
    ON public.itinerary_likes FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can unlike itineraries"
    ON public.itinerary_likes FOR DELETE
    USING (auth.uid() = user_id);

CREATE POLICY "Anyone can see likes"
    ON public.itinerary_likes FOR SELECT
    USING (true);

-- Trip Collaborators
ALTER TABLE public.trip_collaborators ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Owners can manage collaborators"
    ON public.trip_collaborators FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM public.itineraries
            WHERE id = itinerary_id AND user_id = auth.uid()
        )
    )
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.itineraries
            WHERE id = itinerary_id AND user_id = auth.uid()
        )
    );

CREATE POLICY "Collaborators can view trip collaborators"
    ON public.trip_collaborators FOR SELECT
    USING (
        user_id = auth.uid()
        OR EXISTS (
            SELECT 1 FROM public.itineraries
            WHERE id = itinerary_id AND user_id = auth.uid()
        )
        OR EXISTS (
            SELECT 1 FROM public.trip_collaborators tc
            WHERE tc.itinerary_id = trip_collaborators.itinerary_id
              AND tc.user_id = auth.uid()
        )
    );

-- Trip Invites
ALTER TABLE public.trip_invites ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Owners can create and view invites"
    ON public.trip_invites FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM public.itineraries
            WHERE id = itinerary_id AND user_id = auth.uid()
        )
    )
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.itineraries
            WHERE id = itinerary_id AND user_id = auth.uid()
        )
    );

-- Activity Votes
ALTER TABLE public.activity_votes ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Trip members can view votes"
    ON public.activity_votes FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.itineraries
            WHERE id = itinerary_id AND (user_id = auth.uid() OR is_public = true)
        )
        OR EXISTS (
            SELECT 1 FROM public.trip_collaborators
            WHERE itinerary_id = activity_votes.itinerary_id AND user_id = auth.uid()
        )
    );

CREATE POLICY "Trip members can vote"
    ON public.activity_votes FOR INSERT
    WITH CHECK (
        user_id = auth.uid()
        AND (
            EXISTS (
                SELECT 1 FROM public.itineraries
                WHERE id = itinerary_id AND user_id = auth.uid()
            )
            OR EXISTS (
                SELECT 1 FROM public.trip_collaborators
                WHERE itinerary_id = activity_votes.itinerary_id AND user_id = auth.uid()
            )
        )
    );

CREATE POLICY "Users can remove own votes"
    ON public.activity_votes FOR DELETE
    USING (user_id = auth.uid());
