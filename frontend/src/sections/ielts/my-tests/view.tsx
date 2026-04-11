import { useMemo } from 'react';
// @mui
import Container from '@mui/material/Container';
// locales
import { useLocales } from 'src/locales';
// hooks
import {
  useUrlListState,
  useUrlQueryState,
  stringParam,
  useSyncTableWithUrlListState,
} from 'src/hooks/use-url-query-state';
// table
import { useTable } from 'src/components/table';
// api
import { useStudentAttemptsQuery } from '../shared/api/use-ielts';
// components
import { IeltsPageHeader } from '../shared/components';
import { AttemptsTable, FiltersToolbar } from './components';
import { IeltsMyTestsSkeleton } from './skeleton';

// ----------------------------------------------------------------------

export default function IeltsMyTestsView() {
  const { tx } = useLocales();
  const table = useTable({ defaultRowsPerPage: 10, defaultCurrentPage: 0 });
  const listState = useUrlListState({ defaultPageSize: 10, defaultOrdering: '-updated_at' });
  const { values, setValues } = useUrlQueryState({
    module: stringParam('all'),
    status: stringParam('all'),
  });

  useSyncTableWithUrlListState({
    page: listState.page,
    rowsPerPage: listState.rowsPerPage,
    tablePage: table.page,
    tableRowsPerPage: table.rowsPerPage,
    setTablePage: table.setPage,
    setTableRowsPerPage: table.setRowsPerPage,
  });

  const filters = useMemo(
    () => ({
      page: listState.page,
      pageSize: listState.rowsPerPage,
      search: listState.search,
      module: values.module,
      status: values.status,
    }),
    [listState.page, listState.rowsPerPage, listState.search, values.module, values.status]
  );

  const attemptsQuery = useStudentAttemptsQuery(filters);

  return (
    <Container maxWidth="lg">
      <IeltsPageHeader
        title={tx('pages.ielts.my_tests.title')}
        description={tx('pages.ielts.my_tests.description')}
      />

      <FiltersToolbar
        search={listState.search}
        module={values.module}
        status={values.status}
        onSearchChange={listState.setSearch}
        onModuleChange={(value) => setValues({ module: value })}
        onStatusChange={(value) => setValues({ status: value })}
      />

      {attemptsQuery.isLoading || !attemptsQuery.data ? <IeltsMyTestsSkeleton /> : null}

      {attemptsQuery.data ? (
        <AttemptsTable
          items={attemptsQuery.data.results}
          count={attemptsQuery.data.count}
          page={table.page}
          rowsPerPage={table.rowsPerPage}
          dense={table.dense}
          onPageChange={listState.handlePageChange}
          onRowsPerPageChange={listState.handleRowsPerPageChange}
        />
      ) : null}
    </Container>
  );
}
