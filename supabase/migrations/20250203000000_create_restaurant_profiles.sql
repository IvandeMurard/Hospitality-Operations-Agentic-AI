-- IVA-52: Restaurant Profiles table for contextual predictions
-- Run this in Supabase SQL Editor: Dashboard > SQL Editor > New Query

-- Create restaurant_profiles table
CREATE TABLE restaurant_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Identity
    property_name VARCHAR(255) NOT NULL,
    outlet_name VARCHAR(255) NOT NULL,
    outlet_type VARCHAR(50) DEFAULT 'restaurant',  -- restaurant, bar, room_service, pool_bar
    
    -- Capacity
    total_seats INTEGER NOT NULL,
    turns_breakfast DECIMAL(3,1) DEFAULT 1.0,
    turns_lunch DECIMAL(3,1) DEFAULT 1.5,
    turns_dinner DECIMAL(3,1) DEFAULT 2.0,
    
    -- Business Thresholds
    breakeven_covers INTEGER,
    target_covers INTEGER,
    average_ticket DECIMAL(10,2),
    labor_cost_target_pct DECIMAL(5,2),  -- e.g., 28.5 for 28.5%
    
    -- Staffing Ratios (covers per staff member)
    covers_per_server INTEGER DEFAULT 16,
    covers_per_host INTEGER DEFAULT 60,
    covers_per_runner INTEGER DEFAULT 40,
    covers_per_kitchen INTEGER DEFAULT 30,
    min_foh_staff INTEGER DEFAULT 2,
    min_boh_staff INTEGER DEFAULT 2,
    
    -- Hourly Rates (optional, for cost calculations)
    rate_server DECIMAL(10,2),
    rate_host DECIMAL(10,2),
    rate_runner DECIMAL(10,2),
    rate_kitchen DECIMAL(10,2),
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID,  -- Future: link to users table
    
    -- Constraints
    CONSTRAINT valid_seats CHECK (total_seats > 0),
    CONSTRAINT valid_turns CHECK (turns_breakfast >= 0 AND turns_lunch >= 0 AND turns_dinner >= 0),
    CONSTRAINT valid_ratios CHECK (covers_per_server > 0 AND covers_per_kitchen > 0)
);

-- Create index for quick lookups
CREATE INDEX idx_restaurant_profiles_outlet ON restaurant_profiles(property_name, outlet_name);

-- Trigger to update updated_at
CREATE OR REPLACE FUNCTION update_restaurant_profile_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER restaurant_profile_updated
    BEFORE UPDATE ON restaurant_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_restaurant_profile_timestamp();

-- Insert default profile for development
INSERT INTO restaurant_profiles (
    property_name,
    outlet_name,
    outlet_type,
    total_seats,
    turns_dinner,
    breakeven_covers,
    target_covers,
    covers_per_server,
    covers_per_kitchen
) VALUES (
    'The Grand Hotel',
    'Main Restaurant',
    'restaurant',
    80,
    2.0,
    35,
    60,
    16,
    30
);
