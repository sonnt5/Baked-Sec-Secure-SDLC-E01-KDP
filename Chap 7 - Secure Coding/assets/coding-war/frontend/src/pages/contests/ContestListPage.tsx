import { Link } from 'react-router-dom';
import { useContests } from '../../hooks/queries/useContests';

function getContestStatus(contest: any): { label: string; badge: string } {
  const now = new Date();
  const start = new Date(contest.startTime);
  const end = new Date(contest.endTime);

  if (now < start) return { label: 'Upcoming', badge: 'badge-blue' };
  if (now >= start && now <= end) return { label: 'Running', badge: 'badge-green' };
  return { label: 'Ended', badge: 'badge-gray' };
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleString('en-US', {
    month: 'short', day: 'numeric', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  });
}

export default function ContestListPage() {
  const { data, isLoading, isError } = useContests();

  return (
    <div className="content">
      <h1>Contests</h1>

      {isLoading && (
        <div className="panel">
          <div className="panel-body" style={{ textAlign: 'center', padding: 40, color: '#999' }}>
            <span className="spinner" style={{ marginRight: 8 }}></span> Loading contests...
          </div>
        </div>
      )}

      {isError && (
        <div className="alert alert-error">Failed to load contests. Please try again later.</div>
      )}

      {!isLoading && !isError && data && (
        <>
          {data.contests?.length === 0 ? (
            <div className="panel">
              <div className="panel-body" style={{ textAlign: 'center', padding: 40, color: '#999' }}>
                No contests available yet.
              </div>
            </div>
          ) : (
            <div className="panel">
              <table>
                <thead>
                  <tr>
                    <th style={{ width: '40%' }}>Contest</th>
                    <th>Start Time</th>
                    <th>End Time</th>
                    <th>Scoring</th>
                    <th>Participants</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {data.contests?.map((contest: any) => {
                    const status = getContestStatus(contest);
                    return (
                      <tr key={contest.id}>
                        <td>
                          <Link to={`/contests/${contest.id}`} style={{ fontWeight: 500 }}>
                            {contest.title}
                          </Link>
                        </td>
                        <td style={{ fontSize: 12 }}>{formatDate(contest.startTime)}</td>
                        <td style={{ fontSize: 12 }}>{formatDate(contest.endTime)}</td>
                        <td>
                          <span className="badge badge-gray">{contest.scoringType?.toUpperCase() || contest.scoringRule}</span>
                        </td>
                        <td>{contest.participantCount ?? '—'}</td>
                        <td>
                          <span className={`badge ${status.badge}`}>{status.label}</span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </div>
  );
}
