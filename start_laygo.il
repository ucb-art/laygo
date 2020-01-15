/* 
Additional functions for laygo-bag compatiblities, for multiple patterning capabilities.
Load after loading start_bag.il
*/

; Overwrite parse_cad_layout in start_bag.il
procedure( laygo_parse_cad_layout(lib_name cell_name file_name "ttt")
    parse_cad_layout(lib_name cell_name file_name)
)
procedure( parse_cad_layout(lib_name cell_name file_name "ttt")
    let( (cv cell_type p indent rect_cnt label_cnt inst_cnt)

        indent = ""
        cell_type = "layout"
        unless( cv = dbOpenCellViewByType( lib_name cell_name cell_type nil "r" )
            error( "Cannot find layout view of cell %s__%s" lib_name cell_name )
        )
        p = outfile( file_name "w" )

        ; print cellview information
        printf( "*INFO* Writing cell %s__%s (%s) netlist to %s\n" lib_name cell_name cell_type file_name )
        fprintf( p "%slib_name: %s\n" indent lib_name )
        fprintf( p "%scell_name: %s\n" indent cell_name )

        ; print rects
        if( not(cv~>shapes) then
            fprintf( p "%srects: {}\n" indent )
        else
            rect_cnt = 0
            fprintf( p "%srects:\n" indent )
            foreach( shape cv~>shapes
                if( (shape~>objType == "rect") then
                    rect_cnt++ 
                    ; print entry for rect
                    indent = "  "
                    fprintf( p "%s%d:\n" indent rect_cnt )
                    ; print rect master information.
                    indent = "    "
                    fprintf( p "%slayer: %s %s\n" indent nthelem(1 shape~>lpp) nthelem(2 shape~>lpp))
                    fprintf( p "%sbBox: [[%f, %f], [%f, %f]]\n" indent 
                                 nthelem(1 nthelem(1 shape~>bBox)) nthelem(2 nthelem(1 shape~>bBox)) 
                                 nthelem(1 nthelem(2 shape~>bBox)) nthelem(2 nthelem(2 shape~>bBox)) 
                    );fprintf
                    fprintf( p "%scolor: %s \n" indent dbGetShapeColor(shape)) ; added to support MPT
                )
            );if
            if((rect_cnt == 0) then
                fprintf( p "  {}\n" )
           );if
        )

        ; print labels
        indent = ""
        if( not(cv~>shapes) then
            fprintf( p "%slabels: {}\n" indent )
        else
            label_cnt = 0
            fprintf( p "%slabels:\n" indent )
            foreach( shape cv~>shapes
                if( (shape~>objType == "label") then
                    label_cnt++ 
                    ; print entry for label
                    indent = "  "
                    fprintf( p "%s%d:\n" indent label_cnt )
                    ; print label master information.
                    indent = "    "
                    fprintf( p "%slabel: %s\n" indent shape~>theLabel )
                    fprintf( p "%slayer: %s %s\n" indent nthelem(1 shape~>lpp) nthelem(2 shape~>lpp))
                    fprintf( p "%sxy: [%f, %f]\n" indent nthelem(1 shape~>xy) nthelem(2 shape~>xy))
                )
                if( (shape~>objType == "textDisplay") then ;some labels are instantiated as text displays
                    label_cnt++
                    ; print entry for label
                    indent = "  "
                    fprintf( p "%s%d:\n" indent label_cnt )
                    ; print label master information.
                    indent = "    "
                    fprintf( p "%slabel: %s\n" indent shape~>owner~>name )
                    fprintf( p "%slayer: %s %s\n" indent nthelem(1 shape~>lpp) nthelem(2 shape~>lpp))
                    fprintf( p "%sxy: [%f, %f]\n" indent nthelem(1 shape~>xy) nthelem(2 shape~>xy))
                )
            );if
            if((label_cnt == 0) then
                fprintf( p "  {}\n" )
           );if
        )
        
        ; print instances
        indent = ""
        if( not(cv~>instances) then
            fprintf( p "%sinstances: {}\n" indent )
        else
            inst_cnt = 0
            fprintf( p "%sinstances:\n" indent )
            foreach( inst cv~>instances
                inst_cnt++
                ; print entry for instance
                indent = "  "
                fprintf( p "%s%s:\n" indent inst~>name )
                ; print instance master information.
                indent = "    "
                fprintf( p "%slib_name: %s\n" indent inst~>libName )
                fprintf( p "%scell_name: %s\n" indent inst~>cellName )
                fprintf( p "%sxy: [%f, %f]\n" indent nthelem(1 inst~>xy) nthelem(2 inst~>xy))
                if( (inst~>objType == "mosaic") then
                    fprintf( p "%scols: %d\n" indent inst~>columns)
                    fprintf( p "%srows: %d\n" indent inst~>rows)
                    fprintf( p "%ssp_cols: %f\n" indent inst~>uX)
                    fprintf( p "%ssp_rows: %f\n" indent inst~>uY)
                    fprintf( p "%srotation: %s\n" indent car(inst~>tileArray))
                    else
                    fprintf( p "%srotation: %s\n" indent inst~>orient)
                );if
            )
            when(inst_cnt == 0
                fprintf( p "  {}\n" )
            )
        )
        
        ; close resources
        close(p)
        dbClose(cv)
    )
)

; helper for creating a single layout view
procedure( create_layout_helper( cv tech_file inst_list rect_list via_list pin_list path_list "gglllll" )
    let( (inst_cv obj via_def via_enc1 via_enc2 enc1 enc2 off1 off2 via_params make_pin_rect
          pin_bb pin_w pin_h pin_xc pin_yc pin_orient label_h param_order orig_shape arr_dx arr_dy)

        ; create instances
        foreach( inst inst_list
            if( inst_cv = dbOpenCellViewByType( inst->lib inst->cell inst->view nil "r" ) then

                if( and( inst->num_rows==1 inst->num_cols==1) then
                    if( inst->params != nil then
                        ; create pcell instance
                        obj = dbCreateParamInst(cv inst_cv inst->name inst->loc inst->orient 1 inst->params)
                        ; execute parameter callbacks
                        when( obj
                            if( inst->param_order != nil then
                                param_order = inst->param_order
                            else
                                param_order = mapcar( lambda( (x) car(x) ) inst->params )
                            )
                            CCSinvokeCdfCallbacks(obj ?order param_order)
                        )
                    else
                        obj = dbCreateInst(cv inst_cv inst->name inst->loc inst->orient)
                    )
                else
                    if( inst->params != nil then
                        ; create pcell mosaic
                        obj = dbCreateParamSimpleMosaic(cv inst_cv inst->name inst->loc inst->orient
                                                        inst->num_rows inst->num_cols inst->sp_rows inst->sp_cols
                                                        inst->params)
                        ; execute parameter callbacks
                        when( obj
                            if( inst->param_order != nil then
                                param_order = inst->param_order
                            else
                                param_order = mapcar( lambda( (x) car(x) ) inst->params )
                            )
                            CCSinvokeCdfCallbacks(obj ?order param_order)
                        )
                    else
                        obj = dbCreateSimpleMosaic(cv inst_cv inst->name inst->loc inst->orient
                                                   inst->num_rows inst->num_cols inst->sp_rows inst->sp_cols)
                    )
                )
                unless( obj
                    warn("Error creating instance %s of %s__%s (%s).  Skipping." inst->name inst->lib inst->cell inst->view)
                )

            else
                warn("Cannot find instance %s__%s (%s).  Skipping." inst->lib inst->cell inst->view)
            )
        )

        ; create rectangles
        foreach( rect rect_list
            orig_shape = dbCreateRect(cv rect->layer rect->bbox)
            if( rect->color != nil then ; added for MPT
                dbSetShapeColor(orig_shape rect->color)
                dbSetShapeColorLocked(orig_shape t)
            )
            if( not(orig_shape) then
                warn("Error creating rectangle of layer %A.  Skipping." rect->layer)
            else
                when( rect->arr_nx != nil
                    for(icol 2 rect->arr_nx
                        arr_dx = rect->arr_spx * (icol - 1)
                        for(irow 1 rect->arr_ny
                            arr_dy = rect->arr_spy * (irow - 1)
                            dbCopyFig(orig_shape nil list(arr_dx:arr_dy "R0" 1))
                        )
                    )
                    for(irow 2 rect->arr_ny
                        arr_dy = rect->arr_spy * (irow - 1)
                        dbCopyFig(orig_shape nil list(0:arr_dy "R0" 1))
                    )
                )
            )
        )

        ; create paths
        foreach( path path_list
            warn("path creation not implemented yet.  Skipping.")
        )

        ; create vias
        foreach( via via_list
            if( via_def = techFindViaDefByName(tech_file via->id) then
                ; compute via parameter list
                via_enc1 = via->enc1
                via_enc2 = via->enc2
                enc1 = list( (car(via_enc1) + cadr(via_enc1)) / 2.0
                             (caddr(via_enc1) + cadr(cddr(via_enc1))) / 2.0 )
                enc2 = list( (car(via_enc2) + cadr(via_enc2)) / 2.0
                             (caddr(via_enc2) + cadr(cddr(via_enc2))) / 2.0 )
                off1 = list( (cadr(via_enc1) - car(via_enc1)) / 2.0
                             (caddr(via_enc1) - cadr(cddr(via_enc1))) / 2.0 )
                off2 = list( (cadr(via_enc2) - car(via_enc2)) / 2.0
                             (caddr(via_enc2) - cadr(cddr(via_enc2))) / 2.0 )

                via_params = list( list("cutRows" via->num_rows)
                                   list("cutColumns" via->num_cols)
                                   list("cutSpacing" list(via->sp_cols via->sp_rows))
                                   list("layer1Enc" enc1)
                                   list("layer2Enc" enc2)
                                   list("layer1Offset" off1)
                                   list("layer2Offset" off2) )

                ; if via width and height given, add to via_params
                when( via->cut_width != nil
                    via_params = cons( list("cutWidth" via->cut_width) via_params)
                )
                when( via->cut_height != nil
                    via_params = cons( list("cutHeight" via->cut_height) via_params)
                )

                ; create actual via
                orig_shape = dbCreateVia(cv via_def via->loc via->orient via_params)
                if( not(orig_shape) then
                    warn("Error creating via %s.  Skipping." via->id)
                else
                    when( via->arr_nx != nil
                        for(icol 2 via->arr_nx
                            arr_dx = via->arr_spx * (icol - 1)
                            for(irow 1 via->arr_ny
                                arr_dy = via->arr_spy * (irow - 1)
                                dbCopyFig(orig_shape nil list(arr_dx:arr_dy "R0" 1))
                            )
                        )
                        for(irow 2 via->arr_ny
                            arr_dy = via->arr_spy * (irow - 1)
                            dbCopyFig(orig_shape nil list(0:arr_dy "R0" 1))
                        )
                    )
                )
            else
                warn("Via %s not found.  Skipping." via->id)
            )
        )

        ; create pins
        foreach( pin pin_list
            pin_bb = pin->bbox
            pin_w = caadr(pin_bb) - caar(pin_bb)
            pin_h = cadr(cadr(pin_bb)) - cadr(car(pin_bb))
            pin_xc = (caar(pin_bb) + caadr(pin_bb)) / 2.0
            pin_yc = (cadr(car(pin_bb)) + cadr(cadr(pin_bb))) / 2.0

            if( pin_w >= pin_h then
                pin_orient = "R0"
                label_h = pin_h
            else
                pin_orient = "R90"
                label_h = pin_w
            )

            ; get make_pin_rect, true if both net_name and pin_name are non-empty
            make_pin_rect = pin->net_name != "" && pin->pin_name != ""
            when( pin->make_rect != nil
                make_pin_rect = pin->make_rect
            )
            ; printf("make_pin_rect: %A\n" make_pin_rect)
            ; create pin object only if make_pin_rect is True.
            when( make_pin_rect != 0 && make_pin_rect != nil
                ; printf("making pin.\n")
                dbCreatePin( dbMakeNet(cv pin->net_name) dbCreateRect(cv pin->layer pin_bb) pin->pin_name )
            )
            ; printf("%A %A %A %A\n" pin->label pin->layer pin_xc pin_yc)
            dbCreateLabel( cv pin->layer list(pin_xc pin_yc) pin->label "centerCenter" pin_orient "roman" label_h )
        )
    )
)

