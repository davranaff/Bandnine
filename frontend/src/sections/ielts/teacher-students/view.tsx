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
import { useTeacherStudentsQuery } from '../shared/api/use-ielts';
// components
import { IeltsPageHeader } from '../shared/components';
import { StudentsFiltersToolbar, StudentsTable } from './components';
import { IeltsTeacherStudentsSkeleton } from './skeleton';

// ----------------------------------------------------------------------

export default function IeltsTeacherStudentsView() {
  const { tx } = useLocales();
  const table = useTable({ defaultRowsPerPage: 10, defaultCurrentPage: 0 });
  const listState = useUrlListState({ defaultPageSize: 10, defaultOrdering: '-last_activity' });
  const { values, setValues } = useUrlQueryState({
    weakModule: stringParam('all'),
    integrity: stringParam('all'),
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
      weakModule: values.weakModule,
      integrity: values.integrity,
    }),
    [listState.page, listState.rowsPerPage, listState.search, values.integrity, values.weakModule]
  );

  const studentsQuery = useTeacherStudentsQuery(filters);

  return (
    <Container maxWidth="lg">
      <IeltsPageHeader
        title={tx('pages.ielts.teacher.students_title')}
        description={tx('pages.ielts.teacher.students_description')}
      />

      <StudentsFiltersToolbar
        search={listState.search}
        weakModule={values.weakModule}
        integrity={values.integrity}
        onSearchChange={listState.setSearch}
        onWeakModuleChange={(value) => setValues({ weakModule: value })}
        onIntegrityChange={(value) => setValues({ integrity: value })}
      />

      {studentsQuery.isLoading || !studentsQuery.data ? <IeltsTeacherStudentsSkeleton /> : null}

      {studentsQuery.data ? (
        <StudentsTable
          data={studentsQuery.data}
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
