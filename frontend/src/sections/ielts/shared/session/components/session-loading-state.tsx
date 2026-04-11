import Box from '@mui/material/Box';

import { IeltsDetailSkeleton } from '../../skeleton';

export function SessionLoadingState() {
  return (
    <Box sx={{ minHeight: '100dvh', px: { xs: 2, md: 3 }, py: 3 }}>
      <IeltsDetailSkeleton />
    </Box>
  );
}
