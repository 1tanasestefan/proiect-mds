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
    ai_data     JSONB NOT NULL,
    created_at  TIMESTAMPTZ DEFAULT now(),
    updated_at  TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_itineraries_user_id ON public.itineraries(user_id);


-- ┌─────────────────────────────────────────────────────────────┐
-- │  3. COLLECTIONS (folders / wishlists)                      │
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
-- │  4. COLLECTION ↔ ITINERARY (many-to-many join)             │
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
