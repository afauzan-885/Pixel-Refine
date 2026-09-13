def running_median(parent=None, single_process=None, batch_id=None, progress_callback=None, stop_callback=None):
    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.MFDenoiser import running_mf_denoiser
    return running_mf_denoiser(
        parent=parent,
        single_process=single_process,
        batch_id=batch_id,
        progress_callback=progress_callback,
        stop_callback=stop_callback,
        merging_mode="median",
        output_suffix="median"
    )

