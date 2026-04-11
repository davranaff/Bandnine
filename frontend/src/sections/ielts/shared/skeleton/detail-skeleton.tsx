import Skeleton from '@mui/material/Skeleton';
import Stack from '@mui/material/Stack';

export function IeltsDetailSkeleton() {
  return (
    <Stack spacing={3}>
      <Skeleton variant="text" width={320} height={42} />
      <Skeleton variant="rounded" height={160} sx={{ borderRadius: 2 }} />
      <Skeleton variant="rounded" height={220} sx={{ borderRadius: 2 }} />
    </Stack>
  );
}
