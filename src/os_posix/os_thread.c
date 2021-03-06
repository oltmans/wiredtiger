/*-
 * Copyright (c) 2008-2012 WiredTiger, Inc.
 *	All rights reserved.
 *
 * See the file LICENSE for redistribution information.
 */

#include "wt_internal.h"

/*
 * __wt_thread_create --
 *	Create a new thread of control.
 */
int
__wt_thread_create(pthread_t *tidret, void *(*func)(void *), void *arg)
{
	/* Spawn a new thread of control. */
	return ((pthread_create(tidret, NULL, func, arg) == 0) ? 0 : WT_ERROR);
}

/*
 * __wt_thread_join --
 *	Wait for a thread of control to exit.
 */
int
__wt_thread_join(pthread_t tid)
{
	return (pthread_join(tid, NULL) == 0 ? 0 : WT_ERROR);
}
