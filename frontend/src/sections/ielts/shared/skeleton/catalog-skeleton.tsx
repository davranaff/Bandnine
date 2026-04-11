import Grid from '@mui/material/Grid';
import Skeleton from '@mui/material/Skeleton';
import Stack from '@mui/material/Stack';

export function IeltsCatalogSkeleton() {
  return (
    <Stack spacing={3}>
      <Skeleton variant="text" width={260} height={42} />
      <Skeleton variant="rounded" height={88} sx={{ borderRadius: 2 }} />
      <Grid container spacing={3}>
        {[0, 1, 2].map((index) => (
          <Grid key={index} item xs={12} md={6} xl={4}>
            <Skeleton variant="rounded" height={280} sx={{ borderRadius: 2 }} />
          </Grid>
        ))}
      </Grid>
    </Stack>
  );
}
