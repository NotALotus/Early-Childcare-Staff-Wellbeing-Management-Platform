*.js linguist-language=JavaScript

CREATE TABLE notifications (
  id uuid primary key default gen_random_uuid(),
  type text not null,
  message text not null,
  link text,
  is_read boolean default false,
  created_at timestamptz default now()
);
``
