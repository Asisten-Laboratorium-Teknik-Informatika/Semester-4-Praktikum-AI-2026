import { useSyncExternalStore } from 'react'

function subscribe(cb) {
  const mql = window.matchMedia('(max-width: 768px)')
  const mqr = window.matchMedia('(prefers-reduced-motion: reduce)')
  mql.addEventListener('change', cb)
  mqr.addEventListener('change', cb)
  return () => { mql.removeEventListener('change', cb); mqr.removeEventListener('change', cb) }
}

function getSnapshot() {
  const isMobile = window.matchMedia('(max-width: 768px)').matches
  const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  return (isMobile || prefersReduced) ? 'lite' : 'full'
}

export default function useAnimationLevel() {
  return useSyncExternalStore(subscribe, getSnapshot)
}
