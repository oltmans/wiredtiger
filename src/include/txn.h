/*-
 * Copyright (c) 2008-2012 WiredTiger, Inc.
 *	All rights reserved.
 *
 * See the file LICENSE for redistribution information.
 */

/*
 * Transaction ID type: transaction IDs are 32-bit integers that wrap after
 * 4 billion transactions are executed.
 */
typedef uint32_t wt_txnid_t;

#define	WT_TXN_NONE	0		/* No txn running in a session. */
#define	WT_TXN_ABORTED	UINT32_MAX	/* Update rolled back, ignore. */

/*
 * Transaction ID comparison dealing with edge cases and wrapping.
 *
 * WT_TXN_ABORTED is the largest possible ID (never visible to a running
 * transaction), WT_TXN_NONE is smaller than any possible ID (visible to all
 * running transactions).
 *
 * Otherwise, we deal with 32-bit wrapping by looking at the difference between
 * the two IDs.  In what follows, "small" means less than 2^31 and "large"
 * means greater than 2^31.
 *
 * If t2 > t1 and neither has wrapped, then (t2 - t1) is small.  It is
 * certainly smaller than t2, and we assume that we never compare IDs that
 * differ by more than 2^31.  If t2 has wrapped (so it is small) and t1 is
 * large, then (t2 - t1) = (t2 + (-t1)) will be small.
 *
 * In effect, we have a 31-bit window of active transaction IDs: if an update
 * remains in the system after 2 billion transactions it can no longer be
 * compared with current transaction ID.
 */
#define	TXNID_LT(t1, t2)						\
	(((t1) == (t2) ||						\
	 (t1) == WT_TXN_ABORTED || (t2) == WT_TXN_NONE) ? 0 :	\
	 ((t1) == WT_TXN_NONE || (t2) == WT_TXN_ABORTED) ? 1 :	\
	 (t2) - (t1) < (UINT32_MAX / 2))

struct __wt_txn_state {
	wt_txnid_t id;

#define	TXN_STATE_RUNNING	0x01
	uint32_t flags;
};

struct __wt_txn_global {
	volatile wt_txnid_t current;	/* Current transaction ID. */
	WT_TXN_STATE *states;		/* Per-session transaction states */
	wt_txnid_t ckpt_txnid;		/* ID of checkpoint, or WT_TXN_NONE */
};

struct __wt_txn {
	wt_txnid_t id;

	enum {
		TXN_ISO_READ_UNCOMMITTED,
		TXN_ISO_READ_COMMITTED,
		TXN_ISO_SNAPSHOT
	} isolation;

	/*
	 * Snapshot data:
	 *     everything < snapshot[0] is visible,
	 *     everything > id is invisible
	 *     everything in between is visible unless it is in snap_overlap.
	 */
	wt_txnid_t snap_min, snap_max;
	wt_txnid_t *snapshot;
	uint32_t snapshot_count;

	/*
	 * The oldest reader when this transaction started, used to trim
	 * obsolete WT_UPDATE structures.
	 */
	wt_txnid_t oldest_reader;

	/* Array of txn IDs in items created or modified by this txn. */
	wt_txnid_t **mod;
	size_t mod_alloc;
	u_int mod_count;

#define	TXN_ERROR	0x01
#define	TXN_RUNNING	0x02
	uint32_t flags;
};
