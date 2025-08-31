# Supabase Setup Guide

## 1. Create Supabase Project
1. Go to [supabase.com](https://supabase.com)
2. Sign up/Login with GitHub
3. Click "New Project"
4. Choose free tier
5. Enter project name: `bazaarbrain-pro`
6. Set database password (save this!)
7. Choose region closest to your users
8. Wait for setup to complete

## 2. Enable Authentication
1. Go to Authentication → Settings
2. Enable Email auth
3. Configure email templates if needed

## 3. Database Schema

### Users Table
```sql
CREATE TABLE users (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  role VARCHAR(50) DEFAULT 'shopkeeper',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Sales Table
```sql
CREATE TABLE sales (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  product VARCHAR(255) NOT NULL,
  qty INTEGER NOT NULL,
  price DECIMAL(10,2) NOT NULL,
  date DATE NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Queries Table
```sql
CREATE TABLE queries (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  type VARCHAR(100) NOT NULL,
  input TEXT NOT NULL,
  response TEXT,
  date TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## 4. Test Data Insertion
```sql
-- Insert test user
INSERT INTO users (name, email, role) 
VALUES ('Test Shopkeeper', 'test@bazaarbrain.com', 'shopkeeper');

-- Insert test sale
INSERT INTO sales (user_id, product, qty, price, date)
SELECT id, 'Test Product', 5, 10.99, CURRENT_DATE
FROM users WHERE email = 'test@bazaarbrain.com';

-- Insert test query
INSERT INTO queries (user_id, type, input, response)
SELECT id, 'general', 'Hello BazaarBrain', 'Hello! How can I help you today?'
FROM users WHERE email = 'test@bazaarbrain.com';
```

## 5. Get API Keys
1. Go to Settings → API
2. Copy:
   - Project URL
   - Anon Key (public)
   - Service Role Key (keep secret!)
