import { useMemo } from 'react';
// routes
import { paths } from 'src/routes/paths';
// locales
import { useLocales } from 'src/locales';
// components
import SvgColor from 'src/components/svg-color';

// ----------------------------------------------------------------------

const icon = (name: string) => (
  <SvgColor src={`/assets/icons/navbar/${name}.svg`} sx={{ width: 1, height: 1 }} />
);

const ICONS = {
  dashboard: icon('ic_dashboard'),
};

// ----------------------------------------------------------------------

export function useNavData() {
  const { tx } = useLocales();

  const data = useMemo(
    () => [
      {
        subheader: tx('layout.nav.group'),
        items: [
          {
            title: tx('layout.nav.dashboard'),
            path: paths.dashboard,
            icon: ICONS.dashboard,
          },
        ],
      },
    ],
    [tx]
  );

  return data;
}
