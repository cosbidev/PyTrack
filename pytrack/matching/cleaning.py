from pytrack.graph import distance


def veldist_filter(traj, th_dist=5, th_vel=3):
    """ It filters the GPS trajectory combining speed and distance between adjacent points.
    If the adjacent point distance does not exceed the threshold and the speed is less than th_vel (m/s), the current
    trajectory point is ignored.

    Parameters
    ----------
    traj: pandas.DataFrame
        Dataframe containing 3 columns [timestamp, latitude, longitude].
    th_dist: float, optional, default: 5 meters.
        Threshold for the distance of adjacent points.
    th_vel: float, optional, default: 3 m/s.
        Threshold for the velocity.

    Returns
    -------
    df: pandas.DataFrame
        Filtered version of the input dataframe.
    """

    df = traj.copy()

    i = 0
    while True:
        if i == df.shape[0]-1:
            break
        deltat = (df["datetime"][i+1]-df["datetime"][i]).total_seconds()
        dist = distance.haversine_dist(*tuple(df.iloc[i, [1, 2]]), *tuple(df.iloc[i+1, [1, 2]]))

        if dist < th_dist and dist/deltat < th_vel:
            df.drop([i+1], inplace=True)
            df.reset_index(drop=True, inplace=True)
        else:
            i += 1

    return df


def park_filter(traj, th_dist=50, th_time=30):
    """ It removes parking behaviour by eliminating those points that remain in a certain area
    for a given amount of time.

    Parameters
    ----------
    traj: pandas.DataFrame
        Dataframe containing 3 columns [timestamp, latitude, longitude].
    th_dist: float, optional, default: 50 meters.
        Threshold for the distance of adjacent points.
    th_time: float, optional, default: 30 min.
        Threshold for the delta time.

    Returns
    -------
    df: pandas.DataFrame
        Filtered version of the input dataframe.
    """

    df = traj.copy()

    i = 0
    while True:
        if i == df.shape[0]-1:
            break
        deltat = (df["datetime"][i+1]-df["datetime"][i]).total_seconds()
        deltad = distance.haversine_dist(*tuple(df.iloc[i, [1, 2]]), *tuple(df.iloc[i+1, [1, 2]]))

        if deltad < th_dist and deltat > th_time:
            df.drop([i+1], inplace=True)
            df.reset_index(drop=True, inplace=True)
        else:
            i += 1

    return df

