package com.create_skybound.block;

import com.create_skybound.blockentity.DockingClampBlockEntity;
import com.create_skybound.registry.ModBlockEntities;
import com.create_skybound.registry.ModSounds;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.ItemInteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.EntityBlock;
import net.minecraft.world.level.block.RenderShape;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.entity.BlockEntityTicker;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.BooleanProperty;
import net.minecraft.world.level.block.state.properties.DirectionProperty;
import net.minecraft.world.phys.BlockHitResult;
import org.jetbrains.annotations.Nullable;

public class DockingClampBlock extends Block implements EntityBlock {
    public static final DirectionProperty FACING = BlockStateProperties.HORIZONTAL_FACING;
    public static final BooleanProperty LOCKED = BooleanProperty.create("locked");
    public static final BooleanProperty POWERED = BlockStateProperties.POWERED;

    public DockingClampBlock(Properties properties) {
        super(properties);
        this.registerDefaultState(this.stateDefinition.any()
                .setValue(FACING, Direction.NORTH)
                .setValue(LOCKED, false)
                .setValue(POWERED, false));
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(FACING, LOCKED, POWERED);
    }

    @Nullable
    @Override
    public BlockState getStateForPlacement(BlockPlaceContext context) {
        Direction dir = context.getHorizontalDirection().getOpposite();
        boolean powered = context.getLevel().hasNeighborSignal(context.getClickedPos());
        return this.defaultBlockState()
                .setValue(FACING, dir)
                .setValue(POWERED, powered)
                .setValue(LOCKED, powered);
    }

    @Override
    protected void neighborChanged(BlockState state, Level level, BlockPos pos, Block neighborBlock, BlockPos neighborPos, boolean movedByPiston) {
        if (!level.isClientSide) {
            boolean isPowered = level.hasNeighborSignal(pos);
            if (isPowered != state.getValue(POWERED)) {
                boolean wasLocked = state.getValue(LOCKED);
                boolean newLocked = isPowered;
                level.setBlock(pos, state.setValue(POWERED, isPowered).setValue(LOCKED, newLocked), 3);
                if (newLocked != wasLocked) {
                    level.playSound(null, pos, newLocked ? ModSounds.CLAMP_LOCK.get() : ModSounds.CLAMP_UNLOCK.get(),
                            SoundSource.BLOCKS, 1.0f, 1.0f);
                }
            }
        }
    }

    @Override
    protected ItemInteractionResult useItemOn(ItemStack stack, BlockState state, Level level, BlockPos pos, Player player, InteractionHand hand, BlockHitResult hitResult) {
        if (!level.isClientSide) {
            boolean currentLocked = state.getValue(LOCKED);
            boolean nextLocked = !currentLocked;
            level.setBlock(pos, state.setValue(LOCKED, nextLocked), 3);
            level.playSound(null, pos, nextLocked ? ModSounds.CLAMP_LOCK.get() : ModSounds.CLAMP_UNLOCK.get(),
                    SoundSource.BLOCKS, 1.0f, 1.0f);
        }
        return ItemInteractionResult.SUCCESS;
    }

    @Override
    protected RenderShape getRenderShape(BlockState state) {
        return RenderShape.MODEL;
    }

    @Nullable
    @Override
    public BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
        return new DockingClampBlockEntity(pos, state);
    }

    @Nullable
    @Override
    public <T extends BlockEntity> BlockEntityTicker<T> getTicker(Level level, BlockState state, BlockEntityType<T> type) {
        return createTickerHelper(type, ModBlockEntities.DOCKING_CLAMP.get(), DockingClampBlockEntity::tick);
    }

    @SuppressWarnings("unchecked")
    @Nullable
    protected static <E extends BlockEntity, A extends BlockEntity> BlockEntityTicker<A> createTickerHelper(
            BlockEntityType<A> serverType, BlockEntityType<E> clientType, BlockEntityTicker<? super E> ticker) {
        return clientType == serverType ? (BlockEntityTicker<A>) ticker : null;
    }

    @Override
    protected boolean hasAnalogOutputSignal(BlockState state) {
        return true;
    }

    @Override
    protected int getAnalogOutputSignal(BlockState state, Level level, BlockPos pos) {
        BlockEntity be = level.getBlockEntity(pos);
        if (be instanceof DockingClampBlockEntity clamp && clamp.hasDockedVessel()) {
            return 15;
        }
        return state.getValue(LOCKED) ? 7 : 0;
    }
}
