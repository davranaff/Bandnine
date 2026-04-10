// @mui
import { alpha, useTheme } from '@mui/material/styles';
import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import Container from '@mui/material/Container';
import Grid from '@mui/material/Grid';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
// locales
import { useLocales } from 'src/locales';
// components
import Iconify from 'src/components/iconify';

// ----------------------------------------------------------------------

type ModuleCardProps = {
  title: string;
  description: string;
  icon: string;
  colorKey: 'primary' | 'info' | 'success';
};

function ModuleCard({ title, description, icon, colorKey }: ModuleCardProps) {
  const theme = useTheme();
  const palette = theme.palette[colorKey];

  return (
    <Card
      sx={{
        p: 3,
        height: 1,
        cursor: 'default',
        transition: theme.transitions.create(['box-shadow', 'transform']),
        '&:hover': {
          boxShadow: theme.customShadows.z24,
          transform: 'translateY(-4px)',
        },
        border: `1px solid ${alpha(palette.main, 0.12)}`,
        bgcolor: alpha(palette.main, 0.08),
      }}
    >
      <Stack spacing={2}>
        <Box
          sx={{
            width: 56,
            height: 56,
            borderRadius: 1.5,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            bgcolor: alpha(palette.main, 0.16),
            color: `${colorKey}.main`,
          }}
        >
          <Iconify icon={icon} width={32} />
        </Box>
        <Typography variant="h6">{title}</Typography>
        <Typography variant="body2" sx={{ color: 'text.secondary' }}>
          {description}
        </Typography>
      </Stack>
    </Card>
  );
}

// ----------------------------------------------------------------------

export default function IeltsDashboardView() {
  const { tx } = useLocales();

  const modules: ModuleCardProps[] = [
    {
      title: tx('pages.ielts.reading.title'),
      description: tx('pages.ielts.reading.description'),
      icon: 'solar:book-bold-duotone',
      colorKey: 'primary',
    },
    {
      title: tx('pages.ielts.writing.title'),
      description: tx('pages.ielts.writing.description'),
      icon: 'solar:pen-bold-duotone',
      colorKey: 'info',
    },
    {
      title: tx('pages.ielts.listening.title'),
      description: tx('pages.ielts.listening.description'),
      icon: 'solar:headphones-round-bold-duotone',
      colorKey: 'success',
    },
  ];

  return (
    <Container maxWidth="lg">
      <Stack spacing={1} sx={{ mb: 5 }}>
        <Typography variant="h4">{tx('pages.ielts.headline')}</Typography>
        <Typography variant="body2" sx={{ color: 'text.secondary', maxWidth: 640 }}>
          {tx('pages.ielts.subtitle')}
        </Typography>
      </Stack>

      <Grid container spacing={3}>
        {modules.map((m) => (
          <Grid key={m.title} item xs={12} md={4}>
            <ModuleCard {...m} />
          </Grid>
        ))}
      </Grid>
    </Container>
  );
}
