"use client";
import React, { createContext, useContext, useEffect, useState } from 'react';

type OfflineState = {
  unsyncedCount: number;
  addUnsynced: () => void;
  clearUnsynced: () => void;
};

const OfflineContext = createContext<OfflineState | undefined>(undefined);

export function OfflineProvider({ children }: { children: React.ReactNode }) {
  const [unsyncedCount, setUnsyncedCount] = useState(0);

  useEffect(() => {
    const saved = Number(localStorage.getItem('BB_UNSYNCED') || '0');
    setUnsyncedCount(saved);
  }, []);

  const addUnsynced = () => {
    const next = unsyncedCount + 1;
    setUnsyncedCount(next);
    localStorage.setItem('BB_UNSYNCED', String(next));
  };

  const clearUnsynced = () => {
    setUnsyncedCount(0);
    localStorage.setItem('BB_UNSYNCED', '0');
  };

  return (
    <OfflineContext.Provider value={{ unsyncedCount, addUnsynced, clearUnsynced }}>
      {children}
    </OfflineContext.Provider>
  );
}

export function useOffline() {
  const ctx = useContext(OfflineContext);
  if (!ctx) throw new Error('useOffline must be used within OfflineProvider');
  return ctx;
}
